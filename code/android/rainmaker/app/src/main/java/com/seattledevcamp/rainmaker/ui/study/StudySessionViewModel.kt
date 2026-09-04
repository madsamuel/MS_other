package com.seattledevcamp.rainmaker.ui.study

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class StudySessionViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(StudySessionState())
    val uiState: StateFlow<StudySessionState> = _uiState.asStateFlow()

    fun onIntent(intent: StudySessionIntent) {
        when (intent) {
            StudySessionIntent.NextQuestion -> nextQuestion()
            StudySessionIntent.PreviousQuestion -> previousQuestion()
            StudySessionIntent.ToggleAnswer -> toggleAnswer()
            StudySessionIntent.LoadQuestions -> loadQuestions()
            StudySessionIntent.MessageConsumed -> updateState { copy(message = null) }
        }
    }

    private fun nextQuestion() {
        val current = _uiState.value
        if (current.canGoNext) {
            updateState { 
                copy(
                    currentQuestionIndex = currentQuestionIndex + 1,
                    showAnswer = false
                )
            }
        }
    }

    private fun previousQuestion() {
        val current = _uiState.value
        if (current.canGoPrevious) {
            updateState { 
                copy(
                    currentQuestionIndex = currentQuestionIndex - 1,
                    showAnswer = false
                )
            }
        }
    }

    private fun toggleAnswer() {
        updateState { copy(showAnswer = !showAnswer) }
    }

    private fun loadQuestions() {
        viewModelScope.launch {
            updateState { copy(isLoading = true) }
            runCatching {
                val questions = generateSampleQuestions()
                questions
            }.onSuccess { questions ->
                updateState { 
                    copy(
                        isLoading = false, 
                        questions = questions,
                        currentQuestionIndex = 0,
                        showAnswer = false
                    )
                }
            }.onFailure { error ->
                updateState { 
                    copy(
                        isLoading = false, 
                        message = error.message ?: "Failed to load questions"
                    )
                }
            }
        }
    }

    private fun generateSampleQuestions(): List<Question> {
        return listOf(
            Question(1, "A retail business uses past purchase data to estimate future demand. Which analytics category applies?", "Predictive Analytics"),
            Question(2, "Which of the following is NOT a type of data analysis?", "Qualitative Guessing"),
            Question(3, "What is the primary goal of descriptive analytics?", "To summarize historical data"),
            Question(4, "Which analytics type focuses on predicting future outcomes?", "Predictive Analytics"),
            Question(5, "What does prescriptive analytics aim to do?", "Recommend actions based on data")
        )
    }

    private fun updateState(reducer: StudySessionState.() -> StudySessionState) {
        _uiState.value = _uiState.value.reducer()
    }

    init {
        loadQuestions()
    }
}
