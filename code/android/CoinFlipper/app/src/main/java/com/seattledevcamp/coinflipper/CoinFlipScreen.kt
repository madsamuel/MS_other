package com.seattledevcamp.coinflipper

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.animation.core.FastOutSlowInEasing
import android.media.MediaPlayer
import androidx.compose.ui.platform.LocalContext


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CoinFlipScreen(viewModel: CoinFlipViewModel) {
    Scaffold { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Stats section
            StatsSection(viewModel)

            // Coin section
            CoinSection(viewModel)

            // Buttons section
            ButtonsSection(viewModel)
        }
    }
}

@Composable
fun StatsSection(viewModel: CoinFlipViewModel) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Column(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Statistics",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem("Flips", viewModel.flipCount.toString())
                StatItem("Heads", viewModel.headsCount.toString())
                StatItem("Tails", viewModel.tailsCount.toString())
            }
        }
    }
}

@Composable
fun StatItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = label, fontSize = 14.sp)
        Text(text = value, fontSize = 18.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
fun CoinSection(viewModel: CoinFlipViewModel) {
    val isFlipping = viewModel.isFlipping

    // Animation values
    val rotation = remember { Animatable(0f) }
    val scale = remember { Animatable(1f) }

    val context = LocalContext.current
    val mediaPlayer = remember { MediaPlayer.create(context, R.raw.coin_flip) }

    LaunchedEffect(isFlipping) {
        if (isFlipping) {
            mediaPlayer.start()

            // Reset rotation to 0 before starting
            rotation.snapTo(0f)

            // Animate the coin flip
            launch {
                // Scale up slightly
                scale.animateTo(
                    targetValue = 1.2f,
                    animationSpec = tween(durationMillis = 200)
                )

                // Flip the coin (rotate it multiple times)
                rotation.animateTo(
                    targetValue = 1800f, // Multiple full rotations
                    animationSpec = tween(
                        durationMillis = 1000,
                        easing = FastOutSlowInEasing
                    )
                )

                // Scale back to normal
                scale.animateTo(
                    targetValue = 1f,
                    animationSpec = tween(durationMillis = 200)
                )

                // Notify the ViewModel that the animation is complete
                viewModel.onFlipAnimationEnd()
            }
        }
    }

    Box(
        modifier = Modifier
            .size(200.dp)
            .padding(16.dp),
        contentAlignment = Alignment.Center
    ) {
        Image(
            painter = painterResource(
                id = if (viewModel.coinSide == CoinSide.HEADS)
                    R.drawable.heads
                else
                    R.drawable.tails
            ),
            contentDescription = "Coin",
            modifier = Modifier
                .fillMaxSize()
                .scale(scale.value)
                .graphicsLayer {
                    rotationY = rotation.value
                    cameraDistance = 8 * density
                }
        )
    }

    Spacer(modifier = Modifier.height(16.dp))

    Text(
        text = if (isFlipping) "Flipping..." else viewModel.coinSide.name,
        fontSize = 24.sp,
        fontWeight = FontWeight.Bold
    )
}

@Composable
fun ButtonsSection(viewModel: CoinFlipViewModel) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        Button(
            onClick = { viewModel.flipCoin() },
            enabled = !viewModel.isFlipping,
            modifier = Modifier.weight(1f)
        ) {
            Text("Flip Coin")
        }

        Spacer(modifier = Modifier.width(16.dp))

        Button(
            onClick = { viewModel.resetStats() },
            enabled = !viewModel.isFlipping,
            modifier = Modifier.weight(1f)
        ) {
            Text("Reset Stats")
        }
    }
}