// app/src/main/java/com/seattledevcamp/projectmanagementguru/data/dao/QuestionDao.kt
package com.seattledevcamp.projectmanagementguru.data.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.seattledevcamp.projectmanagementguru.data.entities.Question
import kotlinx.coroutines.flow.Flow

@Dao
interface QuestionDao {
    @Query("SELECT * FROM questions WHERE topicId = :topicId")
    fun getQuestionsForTopic(topicId: Long): Flow<List<Question>>

    @Query("SELECT * FROM questions WHERE questionId = :questionId")
    fun getQuestionById(questionId: Long): Flow<Question?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertQuestion(question: Question): Long
}
