package com.seattledevcamp.rainmaker.ui

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.seattledevcamp.rainmaker.ui.generator.GeneratorScreen
import com.seattledevcamp.rainmaker.ui.generator.GeneratorViewModel
import com.seattledevcamp.rainmaker.ui.library.LibraryScreen
import com.seattledevcamp.rainmaker.ui.library.LibraryViewModel

sealed class RainmakerDestination(val route: String) {
    data object Generator : RainmakerDestination("generator")
    data object Library : RainmakerDestination("library")
}

@Composable
fun RainmakerNavHost(modifier: Modifier = Modifier, navController: NavHostController = rememberNavController()) {
    NavHost(
        navController = navController,
        startDestination = RainmakerDestination.Generator.route,
        modifier = modifier
    ) {
        composable(RainmakerDestination.Generator.route) {
            val viewModel: GeneratorViewModel = viewModel()
            val uiState = viewModel.uiState.collectAsStateWithLifecycle()
            GeneratorScreen(
                state = uiState.value,
                onIntent = viewModel::onIntent,
                onLibrary = { navController.navigate(RainmakerDestination.Library.route) }
            )
        }
        composable(RainmakerDestination.Library.route) {
            val viewModel: LibraryViewModel = viewModel()
            val uiState = viewModel.uiState.collectAsStateWithLifecycle()
            LibraryScreen(
                state = uiState.value,
                onIntent = viewModel::onIntent,
                onBack = { navController.popBackStack() }
            )
        }
    }
}
