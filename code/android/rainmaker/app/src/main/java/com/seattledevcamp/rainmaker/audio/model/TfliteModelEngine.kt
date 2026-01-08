package com.seattledevcamp.rainmaker.audio.model

import android.content.Context
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import org.tensorflow.lite.DataType
import org.tensorflow.lite.Interpreter
import java.io.File
import java.io.FileOutputStream
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import kotlin.math.max
import kotlin.math.min

/**
 * TfliteModelEngine: chunked on-device TFLite inference.
 *
 * This implementation requires a TFLite model file present in the APK assets at [modelAssetPath].
 * If the model asset is missing or the interpreter cannot be created, the engine will throw a
 * clear runtime exception with an explanatory message. Procedural generation is intentionally
 * NOT allowed in this strict mode.
 */
class TfliteModelEngine(private val modelAssetPath: String) : ModelAudioEngine {

    @Volatile
    private var interpreter: Interpreter? = null

    private fun loadModelMapped(context: Context): MappedByteBuffer {
        val afd = try {
            context.assets.openFd(modelAssetPath)
        } catch (e: Exception) {
            throw java.io.FileNotFoundException("model-missing:$modelAssetPath")
        }
        FileInputStream(afd.fileDescriptor).channel.use { fc ->
            return fc.map(FileChannel.MapMode.READ_ONLY, afd.startOffset, afd.length)
        }
    }

    private fun ensureInterpreter(context: Context) {
        if (interpreter != null) return
        val model = loadModelMapped(context)
        val options = Interpreter.Options().apply { setNumThreads(2) }
        try {
            interpreter = Interpreter(model, options)
        } catch (e: Exception) {
            // If Interpreter can't be created (missing native libs or incompatible model) rethrow
            throw RuntimeException("failed-to-create-interpreter:${e.message}")
        }
    }

    override suspend fun generate(
        context: Context,
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>,
        durationMinutes: Int,
        seed: Long
    ): File {
        // Require the interpreter; if it's not available, throw descriptive error.
        try {
            ensureInterpreter(context)
        } catch (e: Exception) {
            // Normalize FileNotFoundException into a consistent message for callers
            if (e is java.io.FileNotFoundException && e.message?.startsWith("model-missing:") == true) {
                throw RuntimeException(e.message)
            }
            throw RuntimeException("model-unavailable:${e.message}")
        }

        val interp = interpreter ?: throw RuntimeException("model-unavailable:interpreter-null")

        // Determine model input/output sizes and dtypes
        val inputTensor = interp.getInputTensor(0)
        val outputTensor = interp.getOutputTensor(0)
        val inputShape = inputTensor.shape()
        val outputShape = outputTensor.shape()
        val inputLen = if (inputShape.size >= 2) inputShape[1] else inputShape.reduce { a, b -> a * b }
        val outputLen = if (outputShape.size >= 2) outputShape[1] else outputShape.reduce { a, b -> a * b }

        if (inputTensor.dataType() != DataType.FLOAT32 || outputTensor.dataType() != DataType.FLOAT32) {
            throw IllegalStateException("TFLite model tensors must be FLOAT32 for this engine; found input=${inputTensor.dataType()} output=${outputTensor.dataType()}")
        }

        val sampleRate = 44100
        val totalSeconds = max(1, durationMinutes * 60)
        val totalSamples = totalSeconds * sampleRate

        // We'll run the interpreter over windows of size modelWindow (samples)
        val modelWindow = min(inputLen, outputLen).coerceAtLeast(1)
        if (modelWindow <= 0) throw IllegalStateException("Invalid model IO length: input=$inputLen output=$outputLen")

        // Prepare output file
        val outDir = File(context.filesDir, "rain_records")
        if (!outDir.exists()) outDir.mkdirs()
        val fileName = "rain_${System.currentTimeMillis()}_${seed}.wav"
        val outFile = File(outDir, fileName)

        FileOutputStream(outFile).use { fos ->
            // write WAV header (we know sizes upfront)
            writeWavHeader(fos, totalSamples.toLong(), sampleRate, 1, 16)

            var written = 0
            var chunkIndex = 0

            // Reusable buffers
            val inputBuffer = ByteBuffer.allocateDirect(modelWindow * 4).order(ByteOrder.nativeOrder())
            val outputBuffer = ByteBuffer.allocateDirect(modelWindow * 4).order(ByteOrder.nativeOrder())

            val inputFloats = FloatArray(modelWindow)
            val outputFloats = FloatArray(modelWindow)

            while (written < totalSamples) {
                val remaining = totalSamples - written
                val thisWindow = min(modelWindow, remaining)

                // Prepare input: zero and pack a small header so the model can be conditioned if designed to.
                for (i in 0 until modelWindow) inputFloats[i] = 0f
                if (modelWindow > 0) inputFloats[0] = (seed and 0xffffffffL).toFloat()
                if (modelWindow > 1) inputFloats[1] = chunkIndex.toFloat()
                if (modelWindow > 2) inputFloats[2] = intensity.ordinal.toFloat()
                if (modelWindow > 3) inputFloats[3] = modifiers.fold(0) { acc, m -> acc or m.ordinal } .toFloat()

                inputBuffer.rewind()
                for (i in 0 until modelWindow) inputBuffer.putFloat(inputFloats[i])
                inputBuffer.rewind()

                outputBuffer.rewind()
                try {
                    interp.run(inputBuffer, outputBuffer)
                } catch (e: Exception) {
                    throw RuntimeException("inference-failed:${e.message}")
                }
                outputBuffer.rewind()

                // Read output floats
                for (i in 0 until modelWindow) {
                    outputFloats[i] = outputBuffer.float
                }

                // Convert first thisWindow samples to PCM and write
                val temp = ByteArray(thisWindow * 2)
                var ti = 0
                for (i in 0 until thisWindow) {
                    val f = outputFloats[i]
                    val scaled = (f * Short.MAX_VALUE).toInt()
                    val clamped = max(Short.MIN_VALUE.toInt(), min(Short.MAX_VALUE.toInt(), scaled))
                    val s = clamped.toShort()
                    // little endian
                    temp[ti++] = (s.toInt() and 0xff).toByte()
                    temp[ti++] = ((s.toInt() shr 8) and 0xff).toByte()
                }
                fos.write(temp)

                written += thisWindow
                chunkIndex++
            }
            fos.flush()
        }

        return outFile
    }

    private fun writeWavHeader(out: FileOutputStream, totalSamples: Long, sampleRate: Int, channels: Int, bitsPerSample: Int) {
        val byteRate = sampleRate * channels * bitsPerSample / 8
        val blockAlign = channels * bitsPerSample / 8
        val dataSize = totalSamples * channels * bitsPerSample / 8
        val chunkSize = 36 + dataSize

        val header = ByteBuffer.allocate(44).order(ByteOrder.LITTLE_ENDIAN)
        header.put("RIFF".toByteArray(Charsets.US_ASCII))
        header.putInt(chunkSize.toInt())
        header.put("WAVE".toByteArray(Charsets.US_ASCII))
        header.put("fmt ".toByteArray(Charsets.US_ASCII))
        header.putInt(16) // Subchunk1Size for PCM
        header.putShort(1.toShort()) // AudioFormat = 1 (PCM)
        header.putShort(channels.toShort())
        header.putInt(sampleRate)
        header.putInt(byteRate)
        header.putShort(blockAlign.toShort())
        header.putShort(bitsPerSample.toShort())
        header.put("data".toByteArray(Charsets.US_ASCII))
        header.putInt(dataSize.toInt())
        out.write(header.array())
    }

}
