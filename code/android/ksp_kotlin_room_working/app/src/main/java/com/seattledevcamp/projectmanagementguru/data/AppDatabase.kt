// app/src/main/java/com/seattledevcamp/projectmanagementguru/data/AppDatabase.kt
package com.seattledevcamp.projectmanagementguru.data

import androidx.room.Database
import androidx.room.RoomDatabase
import com.seattledevcamp.projectmanagementguru.data.dao.LessonDao
import com.seattledevcamp.projectmanagementguru.data.dao.TopicDao
import com.seattledevcamp.projectmanagementguru.data.dao.QuestionDao
import com.seattledevcamp.projectmanagementguru.data.entities.Lesson
import com.seattledevcamp.projectmanagementguru.data.entities.Topic
import com.seattledevcamp.projectmanagementguru.data.entities.Question

@Database(entities = [Lesson::class, Topic::class, Question::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun lessonDao(): LessonDao
    abstract fun topicDao(): TopicDao
    abstract fun questionDao(): QuestionDao
}
