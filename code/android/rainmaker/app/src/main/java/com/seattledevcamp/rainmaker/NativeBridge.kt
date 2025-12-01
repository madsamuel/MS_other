package com.seattledevcamp.rainmaker

object NativeBridge {
    // Generates a WAV at `path`, returns true on success
    external fun generate(path: String, sampleRate: Int, durationSec: Int, intensity: Int, modifiersMask: Int): Boolean

    init {
        System.loadLibrary("rain_native")
    }
}

