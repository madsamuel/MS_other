// app/src/main/java/com/seattledevcamp/projectmanagementguru/viewmodel/LessonViewModel.kt
package com.seattledevcamp.projectmanagementguru.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.seattledevcamp.projectmanagementguru.data.entities.Lesson
import com.seattledevcamp.projectmanagementguru.data.repository.ContentRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import javax.inject.Inject

@HiltViewModel
class LessonViewModel @Inject constructor(
    private val repository: ContentRepository
) : ViewModel() {
    val lessons: StateFlow<List<Lesson>> =
        repository.getAllLessons().stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun getTopicCountFlow(lessonId: Long) = repository.getTopicCount(lessonId)
}
