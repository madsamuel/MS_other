package com.seattledevcamp.rainmaker.ui.library

import com.seattledevcamp.rainmaker.data.model.Recording

data class LibraryState(
    val recordings: List<Recording> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

sealed interface LibraryIntent {
    data class Play(val recording: Recording) : LibraryIntent
    data class Delete(val recording: Recording) : LibraryIntent
    data object DismissMessage : LibraryIntent
}

