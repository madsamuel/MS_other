// app/src/main/java/com/seattledevcamp/projectmanagementguru/viewmodel/TopicViewModel.kt
package com.seattledevcamp.projectmanagementguru.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.seattledevcamp.projectmanagementguru.data.entities.Topic
import com.seattledevcamp.projectmanagementguru.data.repository.ContentRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import javax.inject.Inject

@HiltViewModel
class TopicViewModel @Inject constructor(
    private val repository: ContentRepository
) : ViewModel() {
    fun getTopicsForLesson(lessonId: Long): StateFlow<List<Topic>> =
        repository.getTopicsForLesson(lessonId).stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}
