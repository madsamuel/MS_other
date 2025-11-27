package com.seattledevcamp.rainmaker.domain

import com.seattledevcamp.rainmaker.audio.RainAudioEngine
import com.seattledevcamp.rainmaker.data.local.RecordingEntity
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import com.seattledevcamp.rainmaker.data.repository.RecordingRepository

class GenerateRainSoundUseCase(
    private val repository: RecordingRepository,
    private val audioEngine: RainAudioEngine
) {

    suspend operator fun invoke(
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>,
        durationMinutes: Int
    ): RecordingEntity {
        val file = audioEngine.generateAudio(
            intensity = intensity,
            modifiers = modifiers,
            durationMinutes = durationMinutes
        )
        val entity = RecordingEntity(
            title = buildTitle(intensity, modifiers),
            durationMinutes = durationMinutes,
            filePath = file.absolutePath,
            createdAt = System.currentTimeMillis()
        )
        val id = repository.add(entity)
        return entity.copy(id = id)
    }

    private fun buildTitle(
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>
    ): String {
        val base = "${intensity.name.lowercase().replaceFirstChar { it.uppercase() }} rain"
        val modifierText = modifiers.joinToString(", ") { it.name.lowercase().replaceFirstChar(Char::uppercase) }
        return if (modifierText.isBlank()) base else "$base · $modifierText"
    }
}
