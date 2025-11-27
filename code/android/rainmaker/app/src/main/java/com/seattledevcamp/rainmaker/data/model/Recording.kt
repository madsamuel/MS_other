package com.seattledevcamp.rainmaker.data.model

data class Recording(
    val id: Long,
    val title: String,
    val durationMinutes: Int,
    val filePath: String,
    val createdAt: Long
)

