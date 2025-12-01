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

    private var player: MediaPlayer? = null

    init {
        refreshList()
    }

    fun generateRainFile(durationSec: Int, intensityCode: Int, modifiers: Int, filename: String) {
        _status.value = "starting"
        val file = File(getApplication<Application>().filesDir, filename)
        Thread {
            try {
                _status.value = "generating"
                val ok = try {
                    // Call native bridge if available
                    NativeBridge.generate(file.absolutePath, 44100, durationSec, intensityCode, modifiers)
                } catch (_: Throwable) {
                    // Fallback: generate WAV in pure Kotlin
                    val pcm = RainGenerator.generate(44100, durationSec, intensityCode, modifiers)
                    WavWriter.writeWav(getApplication(), filename, 44100, pcm)
                    true
                }
                if (ok) {
                    _status.value = "saved:${file.absolutePath}"
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

    fun playFile(file: File) {
        try {
            player?.release()
            player = MediaPlayer().apply {
                setDataSource(file.absolutePath)
                prepare()
                start()
            }
            _status.value = "playing:${file.name}"
        } catch (e: Exception) {
            _status.value = "error:${e.message}"
        }
    }

    fun deleteFile(file: File) {
        if (file.exists() && file.delete()) {
            _status.value = "deleted:${file.name}"
            refreshList()
        } else {
            _status.value = "error:delete failed"
        }
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
