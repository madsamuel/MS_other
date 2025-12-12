package com.seattledevcamp.rainmaker

object NativeBridge {
    // Existing native signature (no seed)
    external fun generate(path: String, sampleRate: Int, durationSec: Int, intensity: Int, modifiersMask: Int): Boolean

    // Seed-aware native signature (native implementation can optionally provide this)
    external fun generateWithSeed(path: String, sampleRate: Int, durationSec: Int, intensity: Int, modifiersMask: Int, seed: Long): Boolean

    init {
        System.loadLibrary("rain_native")
    }
}
