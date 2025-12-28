package com.seattledevcamp.rainmaker.audio.model

import android.content.Context
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import com.seattledevcamp.rainmaker.audio.WavWriter
import org.tensorflow.lite.Interpreter
import java.io.File
import java.io.FileInputStream
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import kotlin.math.abs

/**
 * TFLite model engine template.
 *
 * IMPORTANT: This implementation assumes a simple model I/O contract for demonstration only:
 * - Input: a float32 array with metadata [intensityCode, modifiersMask, durationSamples, seedLow, seedHigh]
 * - Output: a float32 1-D tensor of PCM samples normalized to [-1,1]
 *
 * Replace the input/output shaping and tensor mapping according to your real model.
 */
class TfliteModelEngine(private val modelAssetPath: String) : ModelAudioEngine {
    @Volatile
    private var interpreter: Interpreter? = null

    private fun loadModelFile(context: Context): MappedByteBuffer {
        val fd = context.assets.openFd(modelAssetPath)
        FileInputStream(fd.fileDescriptor).use { fis ->
            val channel = fis.channel
            return channel.map(FileChannel.MapMode.READ_ONLY, fd.startOffset, fd.length)
        }
    }

    private fun ensureInterpreter(context: Context) {
        if (interpreter == null) {
            val buf = loadModelFile(context)
            interpreter = Interpreter(buf)
        }
    }

    override suspend fun generate(
        context: Context,
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>,
        durationMinutes: Int,
        seed: Long
    ): File {
        ensureInterpreter(context)
        val interp = interpreter ?: throw IllegalStateException("Interpreter not initialized")

        // Chunked generation: split the total duration into smaller chunks (default 5s) and run
        // inference per chunk. This avoids huge memory consumption and allows progress updates.
        val sampleRate = 44100
        val totalSamples = durationMinutes * 60 * sampleRate
        val chunkSec = 5 // seconds per chunk; tune as needed
        val chunkSamplesDefault = chunkSec * sampleRate

        val modifiersMask = modifiers.fold(0) { acc, m ->
            acc or when (m) {
                EnvironmentModifier.SEA -> 1 shl 0
                EnvironmentModifier.CLIFFS -> 1 shl 1
                EnvironmentModifier.FOREST -> 1 shl 2
                EnvironmentModifier.RIVER -> 1 shl 3
                EnvironmentModifier.CITY -> 1 shl 4
                EnvironmentModifier.COUNTRYSIDE -> 1 shl 5
                EnvironmentModifier.CAFE -> 1 shl 6
            }
        }

        val seedLow = (seed and 0xffffffffL).toFloat()
        val seedHigh = ((seed ushr 32) and 0xffffffffL).toFloat()

        // Preallocate final float buffer
        val pcmFloats = FloatArray(totalSamples)

        var written = 0
        var chunkIndex = 0
        while (written < totalSamples) {
            val remaining = totalSamples - written
            val thisChunkSamples = if (remaining >= chunkSamplesDefault) chunkSamplesDefault else remaining

            // Input contract (per-chunk) the model must accept: [intensity, modifiersMask, totalSamples, chunkSamples, chunkIndex, seedLow, seedHigh]
            val input = floatArrayOf(
                intensity.ordinal.toFloat(),
                modifiersMask.toFloat(),
                totalSamples.toFloat(),
                thisChunkSamples.toFloat(),
                chunkIndex.toFloat(),
                seedLow,
                seedHigh
            )

            // Prepare output buffer for this chunk
            val output = Array(1) { FloatArray(thisChunkSamples) }

            // Run interpreter for this chunk. Real model must support this per-chunk API.
            interp.run(input, output)

            // Copy output into final buffer
            val chunkOut = output[0]
            for (i in chunkOut.indices) {
                pcmFloats[written + i] = chunkOut[i]
            }
            written += thisChunkSamples
            chunkIndex++
        }

        // Normalize if needed
        var peak = 0f
        for (v in pcmFloats) peak = kotlin.math.max(peak, abs(v))
        if (peak <= 0f) peak = 1f
        val scale = 0.9f * Short.MAX_VALUE / peak
        val shorts = ShortArray(pcmFloats.size)
        for (i in pcmFloats.indices) shorts[i] = (pcmFloats[i] * scale).toInt().toShort()

        val filename = "recordings/${System.currentTimeMillis()}_tflite.wav"
        val file = File(context.filesDir, filename)
        file.parentFile?.mkdirs()
        WavWriter.writeWav(context, filename.substringAfterLast('/'), sampleRate, shorts)
        return file
    }
}
