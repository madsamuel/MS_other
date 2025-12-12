package com.seattledevcamp.rainmaker.audio

import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.max
import kotlin.random.Random

object RainGenerator {
    data class Layer(val amplitude: Float, val cutoffHz: Float, val density: Float)

    // Added `seed` parameter to guarantee unique output per run when seed differs.
    fun generate(sampleRate: Int = 44100, durationSec: Int = 10, intensity: Int = 1, modifiersMask: Int = 0, seed: Long = Random.nextLong()): ShortArray {
        val totalSamples = sampleRate * durationSec
        // Initialize PRNG with provided seed so same settings + different seed => different audio
        val rnd = Random(seed)
        val mix = FloatArray(totalSamples)

        val layers = when (intensity) {
            0 -> listOf( // light
                Layer(0.4f, 4000f, 0.6f),
                Layer(0.2f, 1200f, 0.3f),
                Layer(0.1f, 8000f, 0.15f)
            )
            2 -> listOf( // heavy
                Layer(0.9f, 6000f, 1.4f),
                Layer(0.5f, 1500f, 0.9f),
                Layer(0.3f, 9000f, 0.35f)
            )
            else -> listOf( // medium
                Layer(0.6f, 5000f, 1.0f),
                Layer(0.35f, 1200f, 0.6f),
                Layer(0.2f, 7000f, 0.25f)
            )
        }

        // apply basic modifier effects
        val adjustedLayers = layers.map { layer ->
            var amp = layer.amplitude
            var density = layer.density
            // forest -> boost mids
            if (modifiersMask and (1 shl 2) != 0) amp *= 1.05f
            // city -> boost highs
            if (modifiersMask and (1 shl 4) != 0) amp *= 1.2f
            Layer(amp, layer.cutoffHz, density)
        }

        for (layer in adjustedLayers) {
            var prev = 0f
            val rc = 1f / (2f * PI.toFloat() * layer.cutoffHz)
            val dt = 1f / sampleRate.toFloat()
            val alpha = dt / (rc + dt)
            for (i in 0 until totalSamples) {
                val white = (rnd.nextFloat() * 2f - 1f) * layer.amplitude
                prev += alpha * (white - prev)
                val env = if (rnd.nextFloat() < (0.002f * layer.density)) 1f else 0.9f
                mix[i] += prev * env
            }
        }

        var peak = 0f
        for (v in mix) peak = max(peak, abs(v))
        if (peak < 1e-6f) peak = 1f
        val scale = 0.9f * Short.MAX_VALUE / peak
        val out = ShortArray(totalSamples)
        for (i in mix.indices) {
            val scaled = (mix[i] * scale).coerceIn(Short.MIN_VALUE.toFloat(), Short.MAX_VALUE.toFloat())
            out[i] = scaled.toInt().toShort()
        }
        return out
    }
}
