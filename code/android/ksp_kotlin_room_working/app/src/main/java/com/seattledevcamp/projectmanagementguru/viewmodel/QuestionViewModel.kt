// app/src/main/java/com/seattledevcamp/projectmanagementguru/viewmodel/QuestionViewModel.kt
package com.seattledevcamp.projectmanagementguru.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.seattledevcamp.projectmanagementguru.data.entities.Question
import com.seattledevcamp.projectmanagementguru.data.repository.ContentRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import javax.inject.Inject

@HiltViewModel
class QuestionViewModel @Inject constructor(
    private val repository: ContentRepository
) : ViewModel() {
    fun getQuestionsForTopic(topicId: Long): StateFlow<List<Question>> =
        repository.getQuestionsForTopic(topicId).stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun getQuestionById(questionId: Long): StateFlow<Question?> =
        repository.getQuestionById(questionId).stateIn(viewModelScope, SharingStarted.Lazily, null)
}
