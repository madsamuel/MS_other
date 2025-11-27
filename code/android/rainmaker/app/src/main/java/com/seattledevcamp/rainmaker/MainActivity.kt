package com.seattledevcamp.rainmaker

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.seattledevcamp.rainmaker.ui.RainmakerNavHost
import com.seattledevcamp.rainmaker.ui.theme.RainmakerTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            RainmakerTheme {
                RainmakerNavHost()
            }
        }
    }
}
