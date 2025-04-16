// app/src/main/java/com/seattledevcamp/projectmanagementguru/data/entities/Question.kt
package com.seattledevcamp.projectmanagementguru.data.entities

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "questions",
    foreignKeys = [
        ForeignKey(
            entity = Topic::class,
            parentColumns = ["topicId"],
            childColumns = ["topicId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("topicId")]
)
data class Question(
    @PrimaryKey(autoGenerate = true) val questionId: Long = 0,
    val questionText: String,
    val answerText: String,
    val topicId: Long
)
