// app/src/main/java/com/seattledevcamp/projectmanagementguru/data/DatabaseSeeder.kt
package com.seattledevcamp.projectmanagementguru.data


import com.seattledevcamp.projectmanagementguru.R
import com.seattledevcamp.projectmanagementguru.data.dao.LessonDao
import com.seattledevcamp.projectmanagementguru.data.dao.TopicDao
import com.seattledevcamp.projectmanagementguru.data.dao.QuestionDao
import com.seattledevcamp.projectmanagementguru.data.entities.Lesson
import com.seattledevcamp.projectmanagementguru.data.entities.Topic
import com.seattledevcamp.projectmanagementguru.data.entities.Question
import kotlinx.coroutines.flow.first
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DatabaseSeeder @Inject constructor(
    private val lessonDao: LessonDao,
    private val topicDao: TopicDao,
    private val questionDao: QuestionDao
) {
    suspend fun seedDatabaseIfEmpty() {
        // Check if the database already has lessons
        val lessons = lessonDao.getAllLessons().first()
        if (lessons.isEmpty()) {
            // Insert a dummy lesson (ensure you have a valid drawable resource, e.g., R.drawable.ic_lesson)
            val lessonId1 = lessonDao.insertLesson(
                Lesson(lessonTitle = "Project Management 101", lessonIcon = R.drawable.ic_lesson)
            )
            // Insert dummy topics for lessonId1
            val topicId1 = topicDao.insertTopic(
                Topic(topicTitle = "Introduction", lessonId = lessonId1)
            )
            val topicId2 = topicDao.insertTopic(
                Topic(topicTitle = "Planning", lessonId = lessonId1)
            )
            // Insert dummy questions for each topic
            questionDao.insertQuestion(
                Question(
                    questionText = "What is project management?",
                    answerText = "Project management is the discipline of planning, executing, and closing projects.",
                    topicId = topicId1
                )
            )
            questionDao.insertQuestion(
                Question(
                    questionText = "What is a project plan?",
                    answerText = "A project plan outlines the objectives, strategies, and tasks for a project.",
                    topicId = topicId2
                )
            )
        }
    }
}