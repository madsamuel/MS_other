package com.seattledevcamp.rainmaker.data.mapper

import com.seattledevcamp.rainmaker.data.local.RecordingEntity
import com.seattledevcamp.rainmaker.data.model.Recording

fun RecordingEntity.toModel(): Recording = Recording(
    id = id,
    title = title,
    durationMinutes = durationMinutes,
    filePath = filePath,
    createdAt = createdAt
)

