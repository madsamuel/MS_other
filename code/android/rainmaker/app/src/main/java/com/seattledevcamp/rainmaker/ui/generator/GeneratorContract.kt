package com.seattledevcamp.rainmaker.ui.generator

import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity

data class GeneratorState(
    val intensity: RainIntensity = RainIntensity.MEDIUM,
    val durationMinutes: Int = 15,
    val modifiers: Set<EnvironmentModifier> = emptySet(),
    val isGenerating: Boolean = false,
    val message: String? = null
)

sealed interface GeneratorIntent {
    data class SelectIntensity(val intensity: RainIntensity) : GeneratorIntent
    data class ToggleModifier(val modifier: EnvironmentModifier) : GeneratorIntent
    data class SetDuration(val minutes: Int) : GeneratorIntent
    data object RequestGenerate : GeneratorIntent
    data object MessageConsumed : GeneratorIntent
}
