package com.seattledevcamp.rainmaker.audio.model

import android.content.Context
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import java.io.File

/**
 * Pluggable model-based audio generation engine.
 * Implementations may use on-device TFLite or cloud inference.
 */
interface ModelAudioEngine {
    /**
     * Generate an audio file using an AI model. Implementations should create and return the file.
     * Throw an exception if model-based generation is unavailable.
     */
    suspend fun generate(
        context: Context,
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>,
        durationMinutes: Int,
        seed: Long
    ): File
}

