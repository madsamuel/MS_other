package com.seattledevcamp.rainmaker.domain

import com.seattledevcamp.rainmaker.data.repository.RecordingRepository

class ObserveRecordingsUseCase(private val repository: RecordingRepository) {
    operator fun invoke() = repository.observeRecordings()
}
