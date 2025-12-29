package com.seattledevcamp.rainmaker

import android.app.Application
import android.media.MediaPlayer
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.File
import com.seattledevcamp.rainmaker.audio.RainAudioEngine
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import com.seattledevcamp.rainmaker.data.model.EnvironmentModifier

class GeneratorViewModel(application: Application, private val audioEngine: RainAudioEngine) : AndroidViewModel(application) {
    private val _status = MutableStateFlow("idle")
    val status = _status.asStateFlow()

    private val _recordings = MutableStateFlow<List<File>>(emptyList())
    val recordings = _recordings.asStateFlow()

    // Playback state
    private val _currentPlaying = MutableStateFlow<String?>(null)
    val currentPlaying = _currentPlaying.asStateFlow()
    private val _isPlaying = MutableStateFlow(false)
    val isPlaying = _isPlaying.asStateFlow()

    private var player: MediaPlayer? = null

    private fun stopPlayback() {
        try {
            val handler = android.os.Handler(android.os.Looper.getMainLooper())
            handler.post {
                try { player?.stop() } catch (_: Exception) {}
                try { player?.release() } catch (_: Exception) {}
                player = null
                _isPlaying.value = false
                _currentPlaying.value = null
                _status.value = "idle"
            }
        } catch (_: Exception) {
            try { player?.stop() } catch (_: Exception) {}
            try { player?.release() } catch (_: Exception) {}
            player = null
            _isPlaying.value = false
            _currentPlaying.value = null
            _status.value = "idle"
        }
    }

    init { refreshList() }

    fun generateRainFile(durationSec: Int, intensityCode: Int, modifiersMask: Int, filename: String, seed: Long = kotlin.random.Random.nextLong()) {
        _status.value = "starting"

        // Map numeric intensity code to data model enum
        val intensity = when (intensityCode) {
            0 -> RainIntensity.LIGHT
            2 -> RainIntensity.HEAVY
            else -> RainIntensity.MEDIUM
        }
        // Convert modifier bitmask to Set<EnvironmentModifier>
        val modifiers = mutableSetOf<EnvironmentModifier>()
        if (modifiersMask and (1 shl 0) != 0) modifiers.add(EnvironmentModifier.SEA)
        if (modifiersMask and (1 shl 1) != 0) modifiers.add(EnvironmentModifier.CLIFFS)
        if (modifiersMask and (1 shl 2) != 0) modifiers.add(EnvironmentModifier.FOREST)
        if (modifiersMask and (1 shl 3) != 0) modifiers.add(EnvironmentModifier.RIVER)
        if (modifiersMask and (1 shl 4) != 0) modifiers.add(EnvironmentModifier.CITY)
        if (modifiersMask and (1 shl 5) != 0) modifiers.add(EnvironmentModifier.COUNTRYSIDE)
        if (modifiersMask and (1 shl 6) != 0) modifiers.add(EnvironmentModifier.CAFE)

        val durationMinutes = (durationSec + 59) / 60

        viewModelScope.launch {
            _status.value = "generating"
            try {
                // Delegate to injected RainAudioEngine (backed by StableAudioEngine via DI)
                val file = audioEngine.generateAudio(intensity, modifiers, durationMinutes)
                _status.value = "saved:${file.absolutePath}:seed=$seed"
            } catch (e: java.io.FileNotFoundException) {
                _status.value = "error:model-missing:${e.message}"
            } catch (e: Exception) {
                _status.value = "error:${e.message}"
            } finally {
                refreshList()
            }
        }
    }

    fun refreshList() {
        val files = getApplication<Application>().filesDir.listFiles { f -> f.extension.equals("wav", ignoreCase = true) }?.toList() ?: emptyList()
        _recordings.value = files.sortedByDescending { it.lastModified() }
    }

    /** Toggle playback for a file: play if not playing, pause if playing the same file, switch otherwise. */
    fun togglePlay(file: File) {
        try {
            val path = file.absolutePath
            // If same file
            if (_currentPlaying.value == path) {
                // toggle pause/resume
                if (player?.isPlaying == true) {
                    player?.pause()
                    _isPlaying.value = false
                    _status.value = "paused:${file.name}"
                } else {
                    player?.start()
                    _isPlaying.value = true
                    _status.value = "playing:${file.name}"
                }
                return
            }

            // Different file: stop previous and start new
            player?.release()
            player = MediaPlayer().apply {
                setDataSource(path)
                // ensure we update state when playback naturally completes
                val fname = file.name
                setOnCompletionListener { mp ->
                    // Ensure we stop and clear playback state when done
                    try { mp.reset(); mp.release() } catch (_: Exception) {}
                    stopPlayback(); refreshList()
                }
                setOnErrorListener { mp, _, _ -> try { mp.reset(); mp.release() } catch (_: Exception) {} ; stopPlayback(); true }
                prepare(); start()
            }
            _currentPlaying.value = path
            _isPlaying.value = true
            _status.value = "playing:${file.name}"
        } catch (e: Exception) {
            _status.value = "error:${e.message}"
        }
    }

    fun deleteFile(file: File) {
        // If deleting the currently playing file, stop playback
        try {
            val path = file.absolutePath
            if (_currentPlaying.value == path) {
                stopPlayback()
            }
        } catch (_: Exception) {
            // ignore
        }

        if (file.exists() && file.delete()) {
            _status.value = "deleted:${file.name}"
            refreshList()
        } else {
            _status.value = "error:delete failed"
        }
    }

    fun updateStatus(message: String) { _status.value = message }

    override fun onCleared() { player?.release(); super.onCleared() }

    class Factory(private val app: Application, private val engine: RainAudioEngine) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return GeneratorViewModel(app, engine) as T
        }
    }
}
