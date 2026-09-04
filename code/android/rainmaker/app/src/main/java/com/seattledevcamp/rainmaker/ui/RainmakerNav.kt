package com.seattledevcamp.rainmaker.ui

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.seattledevcamp.rainmaker.ui.generator.GeneratorScreen
import com.seattledevcamp.rainmaker.ui.generator.GeneratorViewModel
import com.seattledevcamp.rainmaker.ui.library.LibraryScreen
import com.seattledevcamp.rainmaker.ui.library.LibraryViewModel
import com.seattledevcamp.rainmaker.ui.study.StudySessionScreen
import com.seattledevcamp.rainmaker.ui.study.StudySessionViewModel
import org.koin.androidx.compose.koinViewModel

sealed class RainmakerDestination(val route: String) {
    data object Generator : RainmakerDestination("generator")
    data object Library : RainmakerDestination("library")
    data object StudySession : RainmakerDestination("study_session")
}

@Composable
fun RainmakerNavHost(modifier: Modifier = Modifier, navController: NavHostController = rememberNavController()) {
    NavHost(
        navController = navController,
        startDestination = RainmakerDestination.Generator.route,
        modifier = modifier
    ) {
        composable(RainmakerDestination.Generator.route) {
            val viewModel: GeneratorViewModel = koinViewModel()
            val uiState = viewModel.uiState.collectAsStateWithLifecycle()
            GeneratorScreen(
                state = uiState.value,
                onIntent = viewModel::onIntent,
                onLibrary = { navController.navigate(RainmakerDestination.Library.route) },
                onStudySession = { navController.navigate(RainmakerDestination.StudySession.route) }
            )
        }
        composable(RainmakerDestination.Library.route) {
            val viewModel: LibraryViewModel = koinViewModel()
            val uiState = viewModel.uiState.collectAsStateWithLifecycle()
            LibraryScreen(
                state = uiState.value,
                onIntent = viewModel::onIntent,
                onBack = { navController.popBackStack() }
            )
        }
        composable(RainmakerDestination.StudySession.route) {
            val viewModel: StudySessionViewModel = koinViewModel()
            val uiState = viewModel.uiState.collectAsStateWithLifecycle()
            StudySessionScreen(
                state = uiState.value,
                onIntent = viewModel::onIntent,
                onBack = { navController.popBackStack() }
            )
        }
    }
}
