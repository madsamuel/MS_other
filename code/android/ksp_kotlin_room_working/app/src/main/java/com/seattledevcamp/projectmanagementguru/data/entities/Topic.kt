// app/src/main/java/com/seattledevcamp/projectmanagementguru/data/entities/Topic.kt
package com.seattledevcamp.projectmanagementguru.data.entities

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "topics",
    foreignKeys = [
        ForeignKey(
            entity = Lesson::class,
            parentColumns = ["lessonId"],
            childColumns = ["lessonId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("lessonId")]
)
data class Topic(
    @PrimaryKey(autoGenerate = true) val topicId: Long = 0,
    val topicTitle: String,
    val lessonId: Long
)
