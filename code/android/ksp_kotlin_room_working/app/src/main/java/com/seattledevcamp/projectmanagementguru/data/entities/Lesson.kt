package com.seattledevcamp.projectmanagementguru.data.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "lessons")
data class Lesson(
    @PrimaryKey(autoGenerate = true) val lessonId: Long = 0,
    val lessonTitle: String,
    val lessonIcon: Int // This should reference a drawable resource ID (e.g., R.drawable.icon)
)