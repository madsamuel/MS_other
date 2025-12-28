package com.seattledevcamp.rainmaker.audio

import android.content.Context
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import com.seattledevcamp.rainmaker.audio.model.ModelAudioEngine
import kotlinx.coroutines.delay
import java.io.File

class RainAudioEngine(private val context: Context, private val modelEngine: ModelAudioEngine) {

    suspend fun generateAudio(
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>,
        durationMinutes: Int
    ): File {
        // Try model-based generation first; if not available or fails, fall back to procedural generation.
        val seed = kotlin.random.Random.nextLong()
        return try {
            modelEngine.generate(context, intensity, modifiers, durationMinutes, seed)
        } catch (_: Exception) {
            // fallback to procedural generator
            // Keep a small delay to mimic processing and avoid blocking bursts
            delay(500)
            val filename = "recordings/${System.currentTimeMillis()}_proc.wav"
            val file = File(context.filesDir, filename)
            file.parentFile?.mkdirs()
            val pcm = RainGenerator.generate(44100, durationMinutes * 60, intensity.ordinal, modifiersMask(modifiers), seed)
            WavWriter.writeWav(context, filename.substringAfterLast('/'), 44100, pcm)
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
