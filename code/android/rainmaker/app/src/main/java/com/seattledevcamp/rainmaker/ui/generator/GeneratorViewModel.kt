package com.seattledevcamp.rainmaker.ui.generator

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.seattledevcamp.rainmaker.domain.GenerateRainSoundUseCase
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class GeneratorViewModel(
    private val generateRainSound: GenerateRainSoundUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(GeneratorState())
    val uiState: StateFlow<GeneratorState> = _uiState.asStateFlow()

    fun onIntent(intent: GeneratorIntent) {
        when (intent) {
            is GeneratorIntent.SelectIntensity -> updateState { copy(intensity = intent.intensity) }
            is GeneratorIntent.ToggleModifier -> toggleModifier(intent.modifier)
            is GeneratorIntent.SetDuration -> updateState { copy(durationMinutes = intent.minutes) }
            GeneratorIntent.RequestGenerate -> generate()
            GeneratorIntent.MessageConsumed -> updateState { copy(message = null) }
        }
    }

    private fun toggleModifier(modifier: com.seattledevcamp.rainmaker.data.model.EnvironmentModifier) {
        updateState {
            val mods = modifiers.toMutableSet()
            if (mods.contains(modifier)) mods.remove(modifier) else mods.add(modifier)
            copy(modifiers = mods)
        }
    }

    private fun generate() {
        val current = _uiState.value
        if (current.isGenerating) return
        viewModelScope.launch {
            updateState { copy(isGenerating = true, message = null) }
            runCatching {
                generateRainSound(
                    intensity = current.intensity,
                    modifiers = current.modifiers,
                    durationMinutes = current.durationMinutes
                )
            }.onSuccess {
                updateState { copy(isGenerating = false, message = "Recording saved: ${it.title}") }
            }.onFailure { error ->
                updateState { copy(isGenerating = false, message = error.message ?: "Failed to generate") }
            }
        }
    }

    private fun updateState(reducer: GeneratorState.() -> GeneratorState) {
        _uiState.value = _uiState.value.reducer()
    }
}
