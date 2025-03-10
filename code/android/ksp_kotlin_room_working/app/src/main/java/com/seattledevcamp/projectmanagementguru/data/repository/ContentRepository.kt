// app/src/main/java/com/seattledevcamp/projectmanagementguru/data/repository/ContentRepository.kt
package com.seattledevcamp.projectmanagementguru.data.repository

import com.seattledevcamp.projectmanagementguru.data.dao.LessonDao
import com.seattledevcamp.projectmanagementguru.data.dao.TopicDao
import com.seattledevcamp.projectmanagementguru.data.dao.QuestionDao
import javax.inject.Inject

class ContentRepository @Inject constructor(
    private val lessonDao: LessonDao,
    private val topicDao: TopicDao,
    private val questionDao: QuestionDao
) {
    fun getAllLessons() = lessonDao.getAllLessons()
    fun getTopicCount(lessonId: Long) = lessonDao.getTopicCount(lessonId)
    fun getTopicsForLesson(lessonId: Long) = topicDao.getTopicsForLesson(lessonId)
    fun getQuestionsForTopic(topicId: Long) = questionDao.getQuestionsForTopic(topicId)
    fun getQuestionById(questionId: Long) = questionDao.getQuestionById(questionId)
}
