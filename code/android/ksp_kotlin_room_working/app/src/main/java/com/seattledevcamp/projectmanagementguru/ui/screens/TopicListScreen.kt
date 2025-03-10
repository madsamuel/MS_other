// app/src/main/java/com/seattledevcamp/projectmanagementguru/ui/screens/TopicListScreen.kt
package com.seattledevcamp.projectmanagementguru.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.seattledevcamp.projectmanagementguru.data.entities.Topic
import com.seattledevcamp.projectmanagementguru.viewmodel.TopicViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TopicListScreen(
    lessonId: Long,
    onTopicClick: (Long) -> Unit,
    onBack: () -> Unit,
    viewModel: TopicViewModel = hiltViewModel()
) {
    val topics by viewModel.getTopicsForLesson(lessonId).collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Topics") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(modifier = Modifier.padding(padding)) {
            items(topics) { topic: Topic ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(8.dp)
                        .clickable { onTopicClick(topic.topicId) },
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                ) {
                    Text(
                        text = topic.topicTitle,
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.padding(16.dp)
                    )
                }
            }
        }
    }
}
