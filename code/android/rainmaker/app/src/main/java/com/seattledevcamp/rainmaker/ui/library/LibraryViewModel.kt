package com.seattledevcamp.rainmaker.ui.library

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.seattledevcamp.rainmaker.data.local.RecordingEntity
import com.seattledevcamp.rainmaker.data.mapper.toModel
import com.seattledevcamp.rainmaker.data.model.Recording
import com.seattledevcamp.rainmaker.domain.DeleteRecordingUseCase
import com.seattledevcamp.rainmaker.domain.ObserveRecordingsUseCase
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch

class LibraryViewModel(
    private val observeRecordings: ObserveRecordingsUseCase,
    private val deleteRecording: DeleteRecordingUseCase,
    private val player: RainPlayer
) : ViewModel() {

    private val _uiState = MutableStateFlow(LibraryState(isLoading = true))
    val uiState: StateFlow<LibraryState> = _uiState.asStateFlow()

    init {
        observeRecordings()
            .onEach { list ->
                _uiState.value = LibraryState(recordings = list.map { it.toModel() })
            }
            .launchIn(viewModelScope)
    }

    fun onIntent(intent: LibraryIntent) {
        when (intent) {
            is LibraryIntent.Play -> play(intent.recording)
            is LibraryIntent.Delete -> delete(intent.recording)
            LibraryIntent.DismissMessage -> _uiState.value = _uiState.value.copy(errorMessage = null)
        }
    }

    private fun play(recording: Recording) {
        player.play(recording.filePath)
    }

    private fun delete(recording: Recording) {
        viewModelScope.launch {
            val entity = RecordingEntity(
                id = recording.id,
                title = recording.title,
                durationMinutes = recording.durationMinutes,
                filePath = recording.filePath,
                createdAt = recording.createdAt
            )
            runCatching { deleteRecording(entity) }
                .onFailure { error ->
                    _uiState.value = _uiState.value.copy(errorMessage = error.message)
                }
        }
    }
}
