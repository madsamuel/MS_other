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

        // Replace fully-continuous filtered white noise with a drop-based generator plus low-level ambient
        for (layer in adjustedLayers) {
            var prev = 0f
            val rc = 1f / (2f * PI.toFloat() * layer.cutoffHz)
            val dt = 1f / sampleRate.toFloat()
            val alpha = dt / (rc + dt)

            // per-layer drop state
            var dropRemSamples = 0
            var dropTotalSamples = 1
            var dropAmp = 0f

            // base probability per sample for a drop; lowered from previous implementation to avoid near-white noise
            val baseProbPerSample = 0.0002f // ~8.8 drops/sec at density=1 and 44.1kHz

            for (i in 0 until totalSamples) {
                // ambient filtered noise (low-level continuous background)
                val ambientWhite = (rnd.nextFloat() * 2f - 1f) * layer.amplitude * 0.35f
                prev += alpha * (ambientWhite - prev)

                // maybe trigger a drop
                if (dropRemSamples <= 0 && rnd.nextFloat() < (baseProbPerSample * layer.density)) {
                    // drop duration between ~10ms and ~70ms
                    val durSec = 0.01f + rnd.nextFloat() * 0.06f
                    dropTotalSamples = (durSec * sampleRate).toInt().coerceAtLeast(1)
                    dropRemSamples = dropTotalSamples
                    // drop amplitude relative to layer amplitude, add some randomness
                    dropAmp = 0.8f + rnd.nextFloat() * 1.4f
                }

                var dropSample = 0f
                if (dropRemSamples > 0) {
                    val env = dropRemSamples.toFloat() / dropTotalSamples.toFloat() // linear decay envelope
                    val dropWhite = (rnd.nextFloat() * 2f - 1f) * layer.amplitude * dropAmp
                    dropSample = dropWhite * env
                    dropRemSamples--
                }

                // mix: ambient filtered value plus the drop sample (drops are more prominent)
                mix[i] += prev * 0.8f + dropSample
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
