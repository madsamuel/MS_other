package com.seattledevcamp.rainmaker.audio

import android.content.Context
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import com.seattledevcamp.rainmaker.audio.model.ModelAudioEngine
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.delay
import java.io.File

class RainAudioEngine(private val context: Context, private val modelEngine: ModelAudioEngine) {

    suspend fun generateAudio(
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>,
        durationMinutes: Int
    ): File {
        // Run heavy model inference off the main thread to avoid ANR.
        val seed = kotlin.random.Random.nextLong()
        return try {
            withContext(Dispatchers.Default) {
                // Delegate to model engine (may perform heavy tensor ops)
                modelEngine.generate(context, intensity, modifiers, durationMinutes, seed)
            }
        } catch (e: Exception) {
            // fallback to procedural generator on failure - also run off-main and perform IO properly
            // Keep a small delay to mimic processing and avoid blocking bursts
            delay(500)
            val filename = "recordings/${System.currentTimeMillis()}_proc.wav"
            val file = File(context.filesDir, filename)
            file.parentFile?.mkdirs()
            val pcm = withContext(Dispatchers.Default) {
                // Use the context-taking RainGenerator API
                RainGenerator.generate(context, 44100, durationMinutes * 60, intensity.ordinal, modifiersMask(modifiers), seed)
            }
            // write WAV on IO dispatcher
            withContext(Dispatchers.IO) {
                WavWriter.writeWav(context, filename.substringAfterLast('/'), 44100, pcm)
            }
            file
        }
    }

    private fun modifiersMask(mods: Set<EnvironmentModifier>): Int {
        var mask = 0
        for (m in mods) {
            when (m) {
                EnvironmentModifier.SEA -> mask = mask or (1 shl 0)
                EnvironmentModifier.CLIFFS -> mask = mask or (1 shl 1)
                EnvironmentModifier.FOREST -> mask = mask or (1 shl 2)
                EnvironmentModifier.RIVER -> mask = mask or (1 shl 3)
                EnvironmentModifier.CITY -> mask = mask or (1 shl 4)
                EnvironmentModifier.COUNTRYSIDE -> mask = mask or (1 shl 5)
                EnvironmentModifier.CAFE -> mask = mask or (1 shl 6)
            }
        }
        return mask
    }
}
