package com.seattledevcamp.rainmaker.audio.model

import android.content.Context
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import java.io.File
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sin
import kotlin.random.Random

/**
 * Minimal chunked generator placed in `TfliteModelEngine` so all generation paths funnel here.
 *
 * This implementation provides a working on-device generator even when TensorFlow Lite
 * is not available during development. It splits the requested duration into 5s chunks,
 * synthesizes PCM for each chunk (using procedural methods influenced by intensity/modifiers
 * and the provided seed), stitches the chunks and writes a WAV file.
 *
 * The file format is 16-bit PCM, 44100 Hz, mono.
 *
 * If a real TFLite model is added later, this class is the single place to implement
 * the interpreter calls and keep the chunking/stitching logic.
 */
class TfliteModelEngine(private val modelAssetPath: String) : ModelAudioEngine {

    override suspend fun generate(
        context: Context,
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>,
        durationMinutes: Int,
        seed: Long
    ): File {
        // Normalize duration and compute samples
        val sampleRate = 44100
        val totalSeconds = max(1, durationMinutes * 60)
        val totalSamples = totalSeconds * sampleRate

        val chunkSec = 5
        val chunkSamples = chunkSec * sampleRate

        // target directory
        val outDir = File(context.filesDir, "rain_records")
        if (!outDir.exists()) outDir.mkdirs()

        val fileName = "rain_${System.currentTimeMillis()}_${seed}.wav"
        val outFile = File(outDir, fileName)

        // We'll accumulate PCM16 bytes into a ByteBuffer then write a WAV header + data
        val pcmBuffer = ByteBuffer.allocateDirect(totalSamples * 2).order(ByteOrder.LITTLE_ENDIAN)

        var written = 0
        var chunkIndex = 0
        while (written < totalSamples) {
            val remaining = totalSamples - written
            val thisChunkSamples = min(chunkSamples, remaining)
            val chunk = synthesizeChunk(
                sampleRate,
                thisChunkSamples,
                intensity,
                modifiers,
                seed + chunkIndex,
                chunkIndex
            )
            // convert floats (-1..1) to pcm16
            for (s in 0 until thisChunkSamples) {
                val f = chunk[s]
                val v = (max(-1f, min(1f, f)) * Short.MAX_VALUE).toInt().toShort()
                pcmBuffer.putShort(v)
            }
            written += thisChunkSamples
            chunkIndex++
        }

        // write WAV file (header + pcmBuffer)
        pcmBuffer.rewind()
        FileOutputStream(outFile).use { fos ->
            writeWavHeader(fos, totalSamples.toLong(), sampleRate, 1, 16)
            val data = ByteArray(pcmBuffer.remaining())
            pcmBuffer.get(data)
            fos.write(data)
            fos.flush()
        }

        return outFile
    }

    // synthesize a chunk using seeded RNG so repeated runs with same seed produce same output
    private fun synthesizeChunk(
        sampleRate: Int,
        samples: Int,
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>,
        seed: Long,
        chunkIndex: Int
    ): FloatArray {
        val out = FloatArray(samples)
        val rng = Random(seed)

        // intensity base amplitude
        val baseAmp = when (intensity) {
            RainIntensity.LIGHT -> 0.18f
            RainIntensity.MEDIUM -> 0.45f
            RainIntensity.HEAVY -> 0.9f
        }

        // base rain: filtered noise (simple smoothed white noise)
        var prev = 0f
        val smoothFactor = when (intensity) {
            RainIntensity.LIGHT -> 0.995f
            RainIntensity.MEDIUM -> 0.99f
            RainIntensity.HEAVY -> 0.985f
        }

        // modifier influences
        val hasSea = modifiers.contains(EnvironmentModifier.SEA)
        val hasRiver = modifiers.contains(EnvironmentModifier.RIVER)
        val hasForest = modifiers.contains(EnvironmentModifier.FOREST)
        val hasCity = modifiers.contains(EnvironmentModifier.CITY)
        val hasCliffs = modifiers.contains(EnvironmentModifier.CLIFFS)
        val hasCountry = modifiers.contains(EnvironmentModifier.COUNTRYSIDE)
        val hasCafe = modifiers.contains(EnvironmentModifier.CAFE)

        // create deterministic phasors for waves/wind
        val seaPhaseStart = rng.nextDouble() * 2.0 * PI
        val windPhaseStart = rng.nextDouble() * 2.0 * PI

        // small random variation per sample
        for (i in 0 until samples) {
            // white noise
            val white = (rng.nextDouble() * 2.0 - 1.0).toFloat()
            // simple one-pole lowpass to simulate droplet blur
            prev = prev * smoothFactor + white * (1f - smoothFactor)
            var sample = prev

            // apply intensity envelope subtle variation
            val t = i.toFloat() / sampleRate
            val intensityRandom = (sin((t + chunkIndex) * (0.1f + (rng.nextFloat() * 0.05f))).toFloat() * 0.5f + 0.5f)
            sample *= baseAmp * (0.75f + 0.5f * intensityRandom)

            // apply modifiers
            if (hasSea) {
                // waves: low-frequency sine + amplitude modulation
                val waveFreq = 0.15 + rng.nextDouble() * 0.05
                val wave = sin(2.0 * PI * waveFreq * t + seaPhaseStart).toFloat()
                sample += wave * 0.25f * baseAmp
            }

            if (hasRiver) {
                // river: low-pass heavier noise (simulate flow) - use additional smoothed noise
                val riverNoise = (rng.nextDouble() * 2.0 - 1.0).toFloat()
                val river = (riverNoise * 0.5f + sin(2.0 * PI * 1.0 * t).toFloat() * 0.2f) * 0.35f * baseAmp
                sample += river
            }

            if (hasForest) {
                // forest: occasional rustle bursts
                val rustleProb = 0.002 + rng.nextFloat() * 0.003f
                if (rng.nextDouble() < rustleProb) {
                    // short burst
                    val burstLen = (0.1f * sampleRate).toInt().coerceAtLeast(1)
                    val burstAt = i
                    val end = min(samples, burstAt + burstLen)
                    for (j in burstAt until end) {
                        val idx = j - burstAt
                        val env = 1f - idx.toFloat() / burstLen
                        out[j] += ((rng.nextDouble() * 2.0 - 1.0).toFloat() * 0.6f * env * baseAmp)
                    }
                }
            }

            if (hasCity) {
                // city: add discrete metallic taptone events (small probability)
                if (rng.nextDouble() < 0.0006) {
                    // short click
                    val clickLen = 64
                    for (k in 0 until clickLen) {
                        val pos = i + k
                        if (pos >= samples) break
                        val env = 1f - k.toFloat() / clickLen
                        out[pos] += (rng.nextDouble().toFloat() * 0.7f * env * baseAmp)
                    }
                }
            }

            if (hasCliffs) {
                // cliffs: windy low frequency rumble + sharper impacts
                val wind = sin(2.0 * PI * (0.07 + 0.02 * rng.nextDouble()) * t + windPhaseStart).toFloat()
                sample += wind * 0.18f * baseAmp
                if (rng.nextDouble() < 0.0004) {
                    // rock impact
                    val impactLen = 120
                    for (k in 0 until impactLen) {
                        val pos = i + k
                        if (pos >= samples) break
                        val env = 1f - k.toFloat() / impactLen
                        out[pos] += ((rng.nextDouble() * 2.0 - 1.0).toFloat() * 0.9f * env * baseAmp)
                    }
                }
            }

            if (hasCountry) {
                // countryside: wind over fields - gentle low freq noise
                val cw = sin(2.0 * PI * 0.08 * t).toFloat()
                sample += cw * 0.12f * baseAmp
            }

            if (hasCafe) {
                // cafe: distant indoor ambience (low level) - add soft bandpassed noise
                sample += (rng.nextDouble() * 2.0 - 1.0).toFloat() * 0.04f * baseAmp
            }

            // write into out (mix with any previously added bursts)
            out[i] += sample

            // subtle clipping protection
            if (out[i] > 1f) out[i] = 1f
            if (out[i] < -1f) out[i] = -1f
        }

        return out
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
