// app/src/main/java/com/seattledevcamp/projectmanagementguru/data/dao/LessonDao.kt
package com.seattledevcamp.projectmanagementguru.data.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.seattledevcamp.projectmanagementguru.data.entities.Lesson
import kotlinx.coroutines.flow.Flow

@Dao
interface LessonDao {
    @Query("SELECT * FROM lessons")
    fun getAllLessons(): Flow<List<Lesson>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertLesson(lesson: Lesson): Long

    // Query to get count of topics for a given lesson
    @Query("SELECT COUNT(*) FROM topics WHERE lessonId = :lessonId")
    fun getTopicCount(lessonId: Long): Flow<Int>
}
