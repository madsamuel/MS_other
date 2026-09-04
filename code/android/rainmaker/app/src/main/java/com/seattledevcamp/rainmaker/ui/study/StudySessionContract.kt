package com.seattledevcamp.rainmaker.ui.study

data class Question(
    val id: Int,
    val text: String,
    val answer: String
)

data class StudySessionState(
    val questions: List<Question> = emptyList(),
    val currentQuestionIndex: Int = 0,
    val showAnswer: Boolean = false,
    val isLoading: Boolean = false,
    val message: String? = null
) {
    val currentQuestion: Question? = questions.getOrNull(currentQuestionIndex)
    val totalQuestions: Int = questions.size
    val progressText: String = if (totalQuestions > 0) "${currentQuestionIndex + 1} / $totalQuestions" else "0 / 0"
    val canGoNext: Boolean = currentQuestionIndex < totalQuestions - 1
    val canGoPrevious: Boolean = currentQuestionIndex > 0
}

sealed interface StudySessionIntent {
    data object NextQuestion : StudySessionIntent
    data object PreviousQuestion : StudySessionIntent
    data object ToggleAnswer : StudySessionIntent
    data object LoadQuestions : StudySessionIntent
    data object MessageConsumed : StudySessionIntent
}
