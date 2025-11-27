package com.seattledevcamp.rainmaker.domain

import com.seattledevcamp.rainmaker.data.local.RecordingEntity
import com.seattledevcamp.rainmaker.data.repository.RecordingRepository

class DeleteRecordingUseCase(private val repository: RecordingRepository) {
    suspend operator fun invoke(recording: RecordingEntity) {
        repository.delete(recording)
    }
}
