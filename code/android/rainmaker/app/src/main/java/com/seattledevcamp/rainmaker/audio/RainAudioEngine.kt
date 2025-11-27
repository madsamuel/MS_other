package com.seattledevcamp.rainmaker.audio

import android.content.Context
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import kotlinx.coroutines.delay
import java.io.File

class RainAudioEngine(private val context: Context) {

    suspend fun generateAudio(
        intensity: RainIntensity,
        modifiers: Set<EnvironmentModifier>,
        durationMinutes: Int
    ): File {
        delay(1000) // TODO hook into Oboe pipeline
        val file = File(context.filesDir, "recordings/${System.currentTimeMillis()}.wav")
        file.parentFile?.mkdirs()
        file.writeBytes(ByteArray(1024))
        return file
    }
}
