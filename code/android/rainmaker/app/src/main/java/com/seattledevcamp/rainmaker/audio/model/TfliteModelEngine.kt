package com.seattledevcamp.rainmaker.audio.model

import android.content.Context
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import java.io.File

/**
 * Stubbed TFLite model engine used when TensorFlow Lite is not available in the build.
 * This avoids compile/runtime errors when TF Lite is intentionally removed to prevent
 * duplicate-class conflicts. If you want TFLite generation, add the TF Lite dependency
 * and implement the tensor I/O plumbing here.
 */
class TfliteModelEngine(private val modelAssetPath: String) : ModelAudioEngine {
    override suspend fun generate(
        context: Context,
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>,
        durationMinutes: Int,
        seed: Long
    ): File {
        throw UnsupportedOperationException(
            "TFLite model engine is not available in this build. " +
                    "To enable it, add TensorFlow Lite to dependencies and implement TfliteModelEngine.generate accordingly, or use StableAudioEngine."
        )
    }
}
