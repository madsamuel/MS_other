// app/src/main/java/com/seattledevcamp/projectmanagementguru/ui/screens/LessonListScreen.kt
package com.seattledevcamp.projectmanagementguru.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.seattledevcamp.projectmanagementguru.data.entities.Lesson
import com.seattledevcamp.projectmanagementguru.viewmodel.LessonViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LessonListScreen(
    onLessonClick: (Long) -> Unit,
    onSettingsClick: () -> Unit,
    viewModel: LessonViewModel = hiltViewModel()
) {
    val lessons by viewModel.lessons.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Lessons") },
                actions = {
                    IconButton(onClick = onSettingsClick) {
                        Icon(Icons.Default.Settings, contentDescription = "Settings")
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(modifier = Modifier.padding(padding)) {
            items(lessons) { lesson ->
                LessonListItem(lesson = lesson, viewModel = viewModel, onClick = onLessonClick)
            }
        }
    }
}

@Composable
fun LessonListItem(
    lesson: Lesson,
    viewModel: LessonViewModel,
    onClick: (Long) -> Unit
) {
    val topicCount by viewModel.getTopicCountFlow(lesson.lessonId).collectAsState(initial = 0)

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .clickable { onClick(lesson.lessonId) },
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = androidx.compose.ui.Alignment.CenterVertically
        ) {
            Icon(
                painter = painterResource(id = lesson.lessonIcon),
                contentDescription = lesson.lessonTitle,
                modifier = Modifier.size(40.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(text = lesson.lessonTitle, style = MaterialTheme.typography.titleMedium)
                Text(text = "Topics: $topicCount", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
