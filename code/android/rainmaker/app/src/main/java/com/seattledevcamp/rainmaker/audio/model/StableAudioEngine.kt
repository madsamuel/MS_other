package com.seattledevcamp.rainmaker.audio.model

import android.content.Context
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import java.io.File
import java.io.FileOutputStream

/**
 * StableAudioEngine using PyTorch Mobile (TorchScript) for on-device Stable Audio inference.
 * This implementation uses reflection to avoid hard compile-time dependency on PyTorch
 * (helps when the analyzer can't resolve the dependency). At runtime, ensure
 * org.pytorch:pytorch_android_lite is present in the APK.
 */
class StableAudioEngine(private val modelAssetPrefix: String = "stable_audio") : ModelAudioEngine {

    @Volatile
    private var moduleObj: Any? = null
    private var moduleClass: Class<*>? = null
    private var tensorClass: Class<*>? = null
    private var iValueClass: Class<*>? = null

    private fun ensureModel(context: Context): File {
        val modelsDir = File(context.filesDir, "stable_models/$modelAssetPrefix")
        if (!modelsDir.exists()) {
            modelsDir.mkdirs()
            try {
                val assetList = context.assets.list(modelAssetPrefix) ?: emptyArray()
                for (name in assetList) {
                    val out = File(modelsDir, name)
                    context.assets.open("$modelAssetPrefix/$name").use { input ->
                        FileOutputStream(out).use { outStream -> input.copyTo(outStream) }
                    }
                }
            } catch (e: Exception) {
                throw RuntimeException("Failed to extract model assets for $modelAssetPrefix: ${e.message}")
            }
        }
        val modelFile = File(modelsDir, "model.pt")
        if (!modelFile.exists()) throw java.io.FileNotFoundException("TorchScript model not found at ${modelFile.absolutePath}. Place TorchScript model 'model.pt' under assets/$modelAssetPrefix/")
        return modelFile
    }

    private fun ensureModule(context: Context) {
        if (moduleObj == null) {
            val modelFile = ensureModel(context)
            try {
                moduleClass = Class.forName("org.pytorch.Module")
                tensorClass = Class.forName("org.pytorch.Tensor")
                iValueClass = Class.forName("org.pytorch.IValue")

                val loadMethod = moduleClass!!.getMethod("load", String::class.java)
                moduleObj = loadMethod.invoke(null, modelFile.absolutePath)
            } catch (e: ClassNotFoundException) {
                throw RuntimeException("PyTorch classes not available at runtime. Please add org.pytorch:pytorch_android_lite to your app dependencies. Original: ${e.message}")
            }
        }
    }

    override suspend fun generate(context: Context, intensity: RainIntensity, modifiers: Set<EnvironmentModifier>, durationMinutes: Int, seed: Long): File {
        ensureModule(context)
        val modMask = modifiers.fold(0) { acc, m ->
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

        val sampleRate = 44100
        val totalSamples = durationMinutes * 60 * sampleRate
        val chunkSec = 5
        val chunkSamplesDefault = chunkSec * sampleRate

        val outFloats = FloatArray(totalSamples)
        var written = 0
        var chunkIndex = 0
        val mod = moduleObj!!
        val modCls = moduleClass!!
        val tensorCls = tensorClass!!
        val iValCls = iValueClass!!

        while (written < totalSamples) {
            val remaining = totalSamples - written
            val thisChunkSamples = if (remaining >= chunkSamplesDefault) chunkSamplesDefault else remaining

            // Prepare input tensor (1D float array of 7 values)
            val seedLow = (seed and 0xffffffffL).toFloat()
            val seedHigh = ((seed ushr 32) and 0xffffffffL).toFloat()
            val inputArray = floatArrayOf(intensity.ordinal.toFloat(), modMask.toFloat(), totalSamples.toFloat(), thisChunkSamples.toFloat(), chunkIndex.toFloat(), seedLow, seedHigh)

            // Create tensor via reflection: Tensor.fromBlob(float[] data, long[] shape)
            val fromBlobMethod = tensorCls.getMethod("fromBlob", FloatArray::class.java, LongArray::class.java)
            val shape = longArrayOf(1, inputArray.size.toLong())
            val inputTensor = fromBlobMethod.invoke(null, inputArray, shape)

            // Create IValue from tensor: IValue.from(tensor)
            val iValueFromMethod = iValCls.getMethod("from", tensorCls)
            val inputIValue = iValueFromMethod.invoke(null, inputTensor)

            // Call module.forward(IValue) -> IValue
            val forwardMethod = modCls.getMethod("forward", iValCls)
            val resultIValue = forwardMethod.invoke(mod, inputIValue)

            // Convert result to Tensor: resultIValue.toTensor()
            val toTensorMethod = iValCls.getMethod("toTensor")
            val outputTensor = toTensorMethod.invoke(resultIValue)

            // Get float[] from tensor: outputTensor.getDataAsFloatArray()
            val getDataMethod = tensorCls.getMethod("getDataAsFloatArray")
            val chunkOutAny = getDataMethod.invoke(outputTensor) as FloatArray

            // Copy output into final buffer
            for (i in chunkOutAny.indices) outFloats[written + i] = chunkOutAny[i]

            written += thisChunkSamples
            chunkIndex++
        }

        // convert to shorts and write WAV
        var peak = 0f
        for (v in outFloats) peak = kotlin.math.max(peak, kotlin.math.abs(v))
        if (peak <= 0f) peak = 1f
        val scale = 0.9f * Short.MAX_VALUE / peak
        val shorts = ShortArray(outFloats.size)
        for (i in outFloats.indices) shorts[i] = (outFloats[i] * scale).toInt().toShort()

        val filename = "recordings/${System.currentTimeMillis()}_stable.wav"
        val file = File(context.filesDir, filename)
        file.parentFile?.mkdirs()
        com.seattledevcamp.rainmaker.audio.WavWriter.writeWav(context, filename.substringAfterLast('/'), sampleRate, shorts)
        return file
    }
}
