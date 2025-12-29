package com.seattledevcamp.rainmaker

object NativeBridge {
    // Existing native signature (no seed)
    external fun generate(path: String, sampleRate: Int, durationSec: Int, intensity: Int, modifiersMask: Int): Boolean

    // Seed-aware native signature (native implementation can optionally provide this)
    external fun generateWithSeed(path: String, sampleRate: Int, durationSec: Int, intensity: Int, modifiersMask: Int, seed: Long): Boolean

    // Native entrypoint for Stable Audio (ONNX/PyTorch/other) based generation.
    // modelDir is a filesystem path where the model files (converted for mobile) are extracted.
    external fun generateStableAudio(path: String, sampleRate: Int, durationSec: Int, intensity: Int, modifiersMask: Int, seed: Long, modelDir: String): Boolean

    init {
        System.loadLibrary("rain_native")
    }
}
