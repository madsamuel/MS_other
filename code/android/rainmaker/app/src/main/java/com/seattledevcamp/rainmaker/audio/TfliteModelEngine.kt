package com.seattledevcamp.rainmaker.audio

import android.content.Context
import android.annotation.SuppressLint
import kotlinx.coroutines.runBlocking
import java.io.File
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.max

/**
 * Lightweight facade kept for backwards compatibility: provides a generateFull(...) method
 * that delegates to the real `audio.model.TfliteModelEngine` (which implements ModelAudioEngine).
 *
 * Purpose: avoid requiring TensorFlow imports in many places while keeping a simple API
 * that returns raw PCM (ShortArray). This file does not depend on org.tensorflow.lite.
 */
class TfliteModelEngine private constructor(private val context: Context) {
    @SuppressLint("StaticFieldLeak")
    companion object {
        @Volatile
        private var INSTANCE: TfliteModelEngine? = null

        fun getInstance(context: Context): TfliteModelEngine {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: TfliteModelEngine(context.applicationContext).also { INSTANCE = it }
            }
        }
    }

    /**
     * Blocking wrapper that calls the suspend model generator and returns PCM as ShortArray.
     * NOTE: This will block the caller thread until generation completes. Call from a background coroutine.
     */
    @Suppress("UNUSED_PARAMETER")
    fun generateFull(sampleRate: Int, durationSec: Int, intensity: Int, modifiersMask: Int, seed: Long): ShortArray {
        // Use the model engine implementation to produce a WAV file, then read it into ShortArray
        val modelEngine = com.seattledevcamp.rainmaker.audio.model.TfliteModelEngine("rain_model.tflite")

        val durationMinutes = max(1, (durationSec + 59) / 60)

        val outFile: File = runBlocking {
            modelEngine.generate(
                context = context,
                intensity = com.seattledevcamp.rainmaker.data.model.RainIntensity.entries.getOrNull(intensity)
                    ?: com.seattledevcamp.rainmaker.data.model.RainIntensity.MEDIUM,
                modifiers = decodeModifiers(modifiersMask),
                durationMinutes = durationMinutes,
                seed = seed
            )
        }

        return readWavToShortArray(outFile)
    }

    private fun decodeModifiers(mask: Int): Set<com.seattledevcamp.rainmaker.data.model.EnvironmentModifier> {
        val mods = mutableSetOf<com.seattledevcamp.rainmaker.data.model.EnvironmentModifier>()
        com.seattledevcamp.rainmaker.data.model.EnvironmentModifier.entries.forEachIndexed { idx, m ->
            if (mask and (1 shl idx) != 0) mods.add(m)
        }
        return mods
    }

    private fun readWavToShortArray(file: File): ShortArray {
        val fis = FileInputStream(file)
        fis.use { stream ->
            // Skip 44-byte WAV header (assumes PCM 16-bit little-endian)
            val header = ByteArray(44)
            val read = stream.read(header)
            if (read < 44) throw java.io.IOException("Invalid WAV file: too small")

            val remaining = stream.available()
            val data = ByteArray(remaining)
            var off = 0
            while (off < remaining) {
                val r = stream.read(data, off, remaining - off)
                if (r <= 0) break
                off += r
            }

            val samples = data.size / 2
            val out = ShortArray(samples)
            val bb = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)
            for (i in 0 until samples) {
                out[i] = bb.short
            }
            return out
        }
    }

    @Suppress("unused")
    fun close() {
        // no-op facade
    }
}
