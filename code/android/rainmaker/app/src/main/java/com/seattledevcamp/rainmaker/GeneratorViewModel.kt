package com.seattledevcamp.rainmaker

import android.app.Application
import android.media.MediaPlayer
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.File
import com.seattledevcamp.rainmaker.audio.RainGenerator
import com.seattledevcamp.rainmaker.audio.WavWriter

class GeneratorViewModel(application: Application) : AndroidViewModel(application) {
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

    init {
        refreshList()
    }

    fun generateRainFile(durationSec: Int, intensityCode: Int, modifiers: Int, filename: String, seed: Long = kotlin.random.Random.nextLong()) {
        _status.value = "starting"
        val file = File(getApplication<Application>().filesDir, filename)
        Thread {
            try {
                _status.value = "generating"
                val ok = try {
                    // Prefer seed-aware native if present
                    try {
                        NativeBridge.generateWithSeed(file.absolutePath, 44100, durationSec, intensityCode, modifiers, seed)
                    } catch (t: Throwable) {
                        // Fallback to legacy native
                        NativeBridge.generate(file.absolutePath, 44100, durationSec, intensityCode, modifiers)
                    }
                } catch (t: Throwable) {
                    // Fallback: generate WAV in pure Kotlin using provided seed
                    val pcm = RainGenerator.generate(44100, durationSec, intensityCode, modifiers, seed)
                    WavWriter.writeWav(getApplication(), filename, 44100, pcm)
                    true
                }
                if (ok) {
                    _status.value = "saved:${file.absolutePath}:seed=$seed"
                } else {
                    _status.value = "error:native-failed"
                }
            } catch (e: Exception) {
                _status.value = "error:${e.message}"
            } finally {
                refreshList()
            }
        }.start()
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
                prepare()
                start()
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
                player?.stop()
                player?.release()
                player = null
                _currentPlaying.value = null
                _isPlaying.value = false
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

    fun updateStatus(message: String) {
        _status.value = message
    }

    override fun onCleared() {
        player?.release()
        super.onCleared()
    }

    class Factory(private val app: Application) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return GeneratorViewModel(app) as T
        }
    }
}
