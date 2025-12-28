package com.seattledevcamp.rainmaker.audio

import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.sin
import kotlin.random.Random

object RainGenerator {
    data class Layer(val amplitude: Float, val cutoffHz: Float, val density: Float)

    // Added `seed` parameter to guarantee unique output per run when seed differs.
    fun generate(sampleRate: Int = 44100, durationSec: Int = 10, intensity: Int = 1, modifiersMask: Int = 0, seed: Long = Random.nextLong()): ShortArray {
        val totalSamples = sampleRate * durationSec
        // Initialize PRNG with provided seed so same settings + different seed => different audio
        val rnd = Random(seed)
        val mix = FloatArray(totalSamples)

        // Define distinct layer presets per intensity so the overall texture differs noticeably.
        val layers = when (intensity) {
            0 -> listOf( // light: gentle, lower amplitude, sparser drops, brighter
                Layer(0.25f, 6000f, 0.35f),
                Layer(0.12f, 1500f, 0.15f),
                Layer(0.08f, 9000f, 0.08f)
            )
            2 -> listOf( // heavy: loud, dense, with stronger low/mid energy
                Layer(1.0f, 4500f, 1.6f),
                Layer(0.7f, 900f, 1.1f),
                Layer(0.4f, 8000f, 0.5f)
            )
            else -> listOf( // medium: balanced
                Layer(0.6f, 5000f, 1.0f),
                Layer(0.35f, 1200f, 0.6f),
                Layer(0.2f, 7000f, 0.25f)
            )
        }

        // intensity-wide tuning: scale drop probability and drop amplitude ranges so light/medium/heavy behave differently
        val intensityDropProbFactor = when (intensity) {
            0 -> 0.55f
            2 -> 1.6f
            else -> 1.0f
        }
        val dropAmpRange = when (intensity) {
            0 -> Pair(0.5f, 1.0f)
            2 -> Pair(1.2f, 2.4f)
            else -> Pair(0.8f, 1.6f)
        }
        val dropDurRangeSec = when (intensity) {
            0 -> Pair(0.008f, 0.04f)  // shorter, gentle drops
            2 -> Pair(0.02f, 0.12f)   // longer, thunder-like drops
            else -> Pair(0.01f, 0.07f)
        }

        // apply basic modifier effects (environment modifiers influence amplitude/density/cutoff subtly)
        val adjustedLayers = layers.mapIndexed { idx, layer ->
            var amp = layer.amplitude
            var density = layer.density
            var cutoff = layer.cutoffHz

            // sea -> slightly increase density (more continuous rain/sea hiss)
            if (modifiersMask and (1 shl 0) != 0) density *= 1.12f
            // cliffs -> add more mid/low energy
            if (modifiersMask and (1 shl 1) != 0) amp *= 1.08f
            // forest -> boost mids
            if (modifiersMask and (1 shl 2) != 0) amp *= 1.05f
            // river -> increase mid density
            if (modifiersMask and (1 shl 3) != 0) density *= 1.08f
            // city -> boost highs
            if (modifiersMask and (1 shl 4) != 0) amp *= 1.15f
            // countryside -> slightly more spacious (lower density)
            if (modifiersMask and (1 shl 5) != 0) density *= 0.95f
            // cafe -> add a very subtle high-frequency tint
            if (modifiersMask and (1 shl 6) != 0) amp *= 1.02f

            // small per-layer tweak for heavy intensity to deepen low layer
            if (intensity == 2 && idx == 1) {
                cutoff *= 0.9f
                amp *= 1.05f
            }

            Layer(amp, cutoff, density)
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

            // base probability per sample for a drop; tuned low and then scaled by density/intensity
            val baseProbPerSample = 0.00012f // baseline ~5.3 drops/sec at density=1 and 44.1kHz

            for (i in 0 until totalSamples) {
                // ambient filtered noise (low-level continuous background)
                val ambientWhite = (rnd.nextFloat() * 2f - 1f) * layer.amplitude * 0.28f
                prev += alpha * (ambientWhite - prev)

                // maybe trigger a drop: probability scaled by layer density and intensity factor
                if (dropRemSamples <= 0 && rnd.nextFloat() < (baseProbPerSample * layer.density * intensityDropProbFactor)) {
                    // drop duration scaled by intensity
                    val durSec = dropDurRangeSec.first + rnd.nextFloat() * (dropDurRangeSec.second - dropDurRangeSec.first)
                    dropTotalSamples = (durSec * sampleRate).toInt().coerceAtLeast(1)
                    dropRemSamples = dropTotalSamples
                    // drop amplitude relative to layer amplitude, add some randomness
                    val (lowAmp, highAmp) = dropAmpRange
                    dropAmp = lowAmp + rnd.nextFloat() * (highAmp - lowAmp)
                }

                var dropSample = 0f
                if (dropRemSamples > 0) {
                    val env = dropRemSamples.toFloat() / dropTotalSamples.toFloat() // linear decay envelope
                    val dropWhite = (rnd.nextFloat() * 2f - 1f) * layer.amplitude * dropAmp
                    dropSample = dropWhite * env
                    dropRemSamples--
                }

                // mix: ambient filtered value plus the drop sample (drops are more prominent)
                // apply a per-layer weight so low/mid layers feel heavier in heavy intensity
                val layerWeight = when (intensity) {
                    0 -> 0.8f
                    2 -> 1.05f
                    else -> 1.0f
                }
                mix[i] += (prev * 0.75f + dropSample) * layerWeight
            }
        }

        // --- Environment modifiers: add procedural layers for more convincing ambience ---
        val modMix = FloatArray(totalSamples)

        // Helper: simple one-pole lowpass to smooth noise for continuous textures
        fun lowpassWalk(prevIn: Float, alphaLp: Float, input: Float): Float {
            return prevIn + alphaLp * (input - prevIn)
        }

        // SEA: slow swell + filtered wave noise (shore hiss)
        if (modifiersMask and (1 shl 0) != 0) {
            val swellFreq = 0.05f + rnd.nextFloat() * 0.12f // 0.05-0.17 Hz
            var swellPhase = rnd.nextFloat() * 2f * PI.toFloat()
            var lp = 0f
            val lpAlpha = 0.02f
            for (i in 0 until totalSamples) {
                val t = i.toFloat() / sampleRate.toFloat()
                val swell = sin(2.0 * PI * swellFreq * t + swellPhase).toFloat() * 0.6f
                // shore noise: smoothed high-passed noise
                val noise = (rnd.nextFloat() * 2f - 1f) * 0.35f
                lp = lowpassWalk(lp, lpAlpha, noise)
                modMix[i] += swell * 0.7f + (lp * 0.35f)
            }
        }

        // CLIFFS: wind gusts and hard impacts (rock drip)
        if (modifiersMask and (1 shl 1) != 0) {
            var windPrev = 0f
            val windAlpha = 0.003f
            val gustProb = 0.0006f
            for (i in 0 until totalSamples) {
                // continuous wind (low, filtered noise)
                val w = (rnd.nextFloat() * 2f - 1f) * 0.5f
                windPrev = lowpassWalk(windPrev, windAlpha, w)
                var valWind = windPrev * 0.6f
                // occasional rock-impact: sparse impulse with filtered burst
                if (rnd.nextFloat() < 0.00008f) {
                    // short impact burst
                    val burstLen = (0.02f * sampleRate).toInt().coerceAtLeast(1)
                    for (j in 0 until burstLen) {
                        val idx = i + j
                        if (idx < totalSamples) {
                            modMix[idx] += (rnd.nextFloat() * 2f - 1f) * 0.9f * (1f - j.toFloat() / burstLen)
                        }
                    }
                }
                // gusts modulate amplitude
                if (rnd.nextFloat() < gustProb) {
                    val gustLen = (0.3f * sampleRate).toInt()
                    for (j in 0 until gustLen) {
                        val idx = i + j
                        if (idx < totalSamples) modMix[idx] += windPrev * 0.9f * (1f - j.toFloat() / gustLen)
                    }
                }
                modMix[i] += valWind * 0.5f
            }
        }

        // FOREST: rustle of leaves — high-frequency short bursts and low rustle
        if (modifiersMask and (1 shl 2) != 0) {
            val rustleBaseProb = 0.0009f
            for (i in 0 until totalSamples) {
                if (rnd.nextFloat() < rustleBaseProb) {
                    val burstLen = (0.02f + rnd.nextFloat() * 0.08f) * sampleRate
                    val len = burstLen.toInt().coerceAtLeast(1)
                    for (j in 0 until len) {
                        val idx = i + j
                        if (idx < totalSamples) {
                            // higher freq content for rustle
                            modMix[idx] += (rnd.nextFloat() * 2f - 1f) * 0.35f * (1f - j.toFloat() / len)
                        }
                    }
                }
                // subtle continuous rustle
                modMix[i] += (rnd.nextFloat() * 2f - 1f) * 0.02f
            }
        }

        // RIVER: continuous flowing water (low-mid filtered noise with subtle modulation)
        if (modifiersMask and (1 shl 3) != 0) {
            var riverPrev = 0f
            val riverAlpha = 0.01f
            val modSpeed = 0.2f + rnd.nextFloat() * 0.8f
            for (i in 0 until totalSamples) {
                val n = (rnd.nextFloat() * 2f - 1f) * 0.4f
                riverPrev = lowpassWalk(riverPrev, riverAlpha, n)
                val env = (sin(2.0 * PI * modSpeed * i / sampleRate).toFloat() * 0.5f + 0.5f)
                modMix[i] += riverPrev * 0.6f * env
            }
        }

        // CITY: rain on concrete — sharper high-frequency reflections and metallic taps
        if (modifiersMask and (1 shl 4) != 0) {
            val tapProb = 0.0005f
            for (i in 0 until totalSamples) {
                if (rnd.nextFloat() < tapProb) {
                    val tapLen = (0.005f * sampleRate).toInt().coerceAtLeast(1)
                    for (j in 0 until tapLen) {
                        val idx = i + j
                        if (idx < totalSamples) {
                            // bright, short click
                            modMix[idx] += (rnd.nextFloat() * 2f - 1f) * 0.6f * (1f - j.toFloat() / tapLen)
                        }
                    }
                }
                // continuous concrete hiss
                modMix[i] += (rnd.nextFloat() * 2f - 1f) * 0.015f
            }
        }

        // COUNTRYSIDE: wind over fields — long slow gusts and very subtle tones
        if (modifiersMask and (1 shl 5) != 0) {
            val gustBaseProb = 0.0004f
            for (i in 0 until totalSamples) {
                if (rnd.nextFloat() < gustBaseProb) {
                    val gustLen = (0.4f * sampleRate).toInt().coerceAtLeast(1)
                    for (j in 0 until gustLen) {
                        val idx = i + j
                        if (idx < totalSamples) {
                            val f = (j.toFloat() / gustLen)
                            modMix[idx] += (rnd.nextFloat() * 2f - 1f) * 0.5f * (1f - f)
                        }
                    }
                }
                // subtle background wind
                modMix[i] += (rnd.nextFloat() * 2f - 1f) * 0.01f
            }
        }

        // CAFE (treated like small human ambient/high freq tints) -> small high freq background
        if (modifiersMask and (1 shl 6) != 0) {
            for (i in 0 until totalSamples) {
                modMix[i] += (rnd.nextFloat() * 2f - 1f) * 0.02f
            }
        }

        // Mix environment contribution into main mix with a moderate scaling so it is audible but not overpowering
        val envScale = 0.9f
        for (i in 0 until totalSamples) mix[i] += modMix[i] * envScale

        // Final normalization to 16-bit PCM range
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
