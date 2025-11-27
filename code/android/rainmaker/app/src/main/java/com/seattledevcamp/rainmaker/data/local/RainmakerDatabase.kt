package com.seattledevcamp.rainmaker.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [RecordingEntity::class], version = 1, exportSchema = true)
abstract class RainmakerDatabase : RoomDatabase() {
    abstract fun recordingDao(): RecordingDao
}

