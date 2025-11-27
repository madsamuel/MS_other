package com.seattledevcamp.rainmaker.data.repository

import com.seattledevcamp.rainmaker.data.local.RecordingDao
import com.seattledevcamp.rainmaker.data.local.RecordingEntity
import kotlinx.coroutines.flow.Flow

class RecordingRepository(private val dao: RecordingDao) {

    fun observeRecordings(): Flow<List<RecordingEntity>> = dao.observeRecordings()

    suspend fun add(recording: RecordingEntity): Long = dao.insert(recording)

    suspend fun delete(recording: RecordingEntity) {
        dao.delete(recording)
    }
}
