// app/src/main/java/com/seattledevcamp/projectmanagementguru/data/dao/TopicDao.kt
package com.seattledevcamp.projectmanagementguru.data.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.seattledevcamp.projectmanagementguru.data.entities.Topic
import kotlinx.coroutines.flow.Flow

@Dao
interface TopicDao {
    @Query("SELECT * FROM topics WHERE lessonId = :lessonId")
    fun getTopicsForLesson(lessonId: Long): Flow<List<Topic>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTopic(topic: Topic): Long
}
