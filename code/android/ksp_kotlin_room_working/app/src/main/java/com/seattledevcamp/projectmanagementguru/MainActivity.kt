package com.seattledevcamp.projectmanagementguru

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import com.seattledevcamp.projectmanagementguru.ui.theme.ProjectManagementGuruTheme
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import com.seattledevcamp.projectmanagementguru.data.DatabaseSeeder
import com.seattledevcamp.projectmanagementguru.ui.navigation.AppNavHost
import javax.inject.Inject
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var databaseSeeder: DatabaseSeeder

    override fun onCreate(savedInstanceState: Bundle?) {
        // Install the native Android 12+ splash screen
        installSplashScreen()
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()


        // Seed the database with dummy content if empty
        lifecycleScope.launch {
            databaseSeeder.seedDatabaseIfEmpty()
        }


        setContent {
            ProjectManagementGuruTheme {
                // Your UI (for testing, we use a simple Greeting)
//                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
//                    Greeting(name = "Android", modifier = Modifier.padding(innerPadding))
//                }
                AppNavHost()
            }
        }

    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    ProjectManagementGuruTheme {
        Greeting("Android")
    }
}