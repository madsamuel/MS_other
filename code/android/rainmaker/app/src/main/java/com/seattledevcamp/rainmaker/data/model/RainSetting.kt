package com.seattledevcamp.rainmaker.data.model

enum class RainIntensity { LIGHT, MEDIUM, HEAVY }

enum class EnvironmentModifier {
    SEA,
    CLIFFS,
    FOREST,
    RIVER,
    CITY,
    COUNTRYSIDE,
    CAFE
}

data class RainPreset(
    val intensity: RainIntensity,
    val modifiers: Set<EnvironmentModifier> = emptySet(),
    val durationMinutes: Int
)

