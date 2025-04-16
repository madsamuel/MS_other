// app/src/main/java/com/seattledevcamp/projectmanagementguru/ui/screens/AnswerScreen.kt
package com.seattledevcamp.projectmanagementguru.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.seattledevcamp.projectmanagementguru.viewmodel.QuestionViewModel


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnswerScreen(
    questionId: Long,
    onBack: () -> Unit,
    viewModel: QuestionViewModel = hiltViewModel()
) {
    val question by viewModel.getQuestionById(questionId).collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Answer") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentAlignment = Alignment.Center
        ) {
            if (question != null) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = "Q: ${question!!.questionText}", style = MaterialTheme.typography.titleMedium)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = "A: ${question!!.answerText}", style = MaterialTheme.typography.bodyLarge)
                }
            } else {
                CircularProgressIndicator()
            }
        }
    }
}
