// app/src/main/java/com/seattledevcamp/projectmanagementguru/ui/navigation/AppNavHost.kt
package com.seattledevcamp.projectmanagementguru.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.*
import androidx.navigation.navArgument
import com.seattledevcamp.projectmanagementguru.ui.screens.AnswerScreen
import com.seattledevcamp.projectmanagementguru.ui.screens.LessonListScreen
import com.seattledevcamp.projectmanagementguru.ui.screens.QuestionListScreen
import com.seattledevcamp.projectmanagementguru.ui.screens.TopicListScreen
import com.seattledevcamp.projectmanagementguru.ui.screens.SettingsScreen

@Composable
fun AppNavHost() {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = "lesson_list") {
        composable("lesson_list") {
            LessonListScreen(
                onLessonClick = { lessonId ->
                    navController.navigate("topic_list/$lessonId")
                },
                onSettingsClick = { navController.navigate("settings") }
            )
        }
        composable(
            "topic_list/{lessonId}",
            arguments = listOf(navArgument("lessonId") { type = NavType.LongType })
        ) { backStackEntry ->
            val lessonId = backStackEntry.arguments?.getLong("lessonId") ?: 0L
            TopicListScreen(
                lessonId = lessonId,
                onTopicClick = { topicId ->
                    navController.navigate("question_list/$topicId")
                },
                onBack = { navController.popBackStack() }
            )
        }
        composable(
            "question_list/{topicId}",
            arguments = listOf(navArgument("topicId") { type = NavType.LongType })
        ) { backStackEntry ->
            val topicId = backStackEntry.arguments?.getLong("topicId") ?: 0L
            QuestionListScreen(
                topicId = topicId,
                onQuestionClick = { questionId ->
                    navController.navigate("answer/$questionId")
                },
                onBack = { navController.popBackStack() }
            )
        }
        composable(
            "answer/{questionId}",
            arguments = listOf(navArgument("questionId") { type = NavType.LongType })
        ) { backStackEntry ->
            val questionId = backStackEntry.arguments?.getLong("questionId") ?: 0L
            AnswerScreen(
                questionId = questionId,
                onBack = { navController.popBackStack() }
            )
        }
        composable("settings") {
            SettingsScreen(onBack = { navController.popBackStack() })
        }
    }
}
