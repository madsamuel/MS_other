package com.seattledevcamp.rainmaker.audio

import android.content.Context

/**
 * Legacy entrypoint name kept for compatibility; generation now delegates to a TFLite engine.
 * NOTE: callers must pass an Android Context so the TFLite model asset can be loaded.
 */
object RainGenerator {

    /**
     * Generate PCM using the on-device TFLite model.
     * This replaces the old procedural generator and requires a Context to access assets.
     *
     * @param context Android Context used to load the TFLite model asset ("rain_model.tflite").
     * @param sampleRate audio sample rate (defaults to 44100)
     * @param durationSec duration in seconds
     * @param intensity 0=light,1=medium,2=heavy
     * @param modifiersMask bitmask for environment modifiers (sea, cliffs, forest, ...)
     * @param seed deterministic seed; different seed -> unique audio even with same settings
     * @return interleaved mono 16-bit PCM in ShortArray
     * @throws IllegalStateException if model asset cannot be found or inference fails
     */
    @JvmStatic
    fun generate(
        context: Context,
        sampleRate: Int = 44100,
        durationSec: Int = 10,
        intensity: Int = 1,
        modifiersMask: Int = 0,
        seed: Long = kotlin.random.Random.nextLong()
    ): ShortArray {
        // Delegate to the TFLite-based engine. This centralizes model usage in one place.
        val engine = com.seattledevcamp.rainmaker.audio.TfliteModelEngine.getInstance(context)
        return engine.generateFull(sampleRate, durationSec, intensity, modifiersMask, seed)
    }

    /**
     * Compatibility helper: callers that cannot immediately pass a Context should update to use
     * the Context-taking overload. Calling this will throw and guide the developer.
     */
    @Deprecated("Use generate(context, ...) instead")
    fun generate(sampleRate: Int = 44100, durationSec: Int = 10, intensity: Int = 1, modifiersMask: Int = 0, seed: Long = 0L): ShortArray {
        throw IllegalStateException("RainGenerator.generate(...) without Context has been removed. Call RainGenerator.generate(context, ...) so the app can load the rain_model.tflite asset.")
    }
}
