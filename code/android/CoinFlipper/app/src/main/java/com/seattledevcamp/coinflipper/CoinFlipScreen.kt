package com.seattledevcamp.coinflipper

import android.media.MediaPlayer
import android.util.Log
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.sp
import kotlin.math.PI
import kotlin.math.sin

@Composable
fun CoinFlipScreen(viewModel: CoinFlipViewModel) {
    val colors = MaterialTheme.colorScheme
    Scaffold(containerColor = colors.background) { padding ->
        BoxWithConstraints(
            Modifier.fillMaxSize().padding(padding)
        ) {
            val coinSize = (maxHeight - 600.dp).coerceIn(160.dp, 264.dp)
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 24.dp, vertical = 16.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Row(
                    Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    GoldCoin(CoinSide.HEADS, Modifier.size(32.dp))
                    Text(
                        stringResource(R.string.app_name),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                }
                Column(
                    Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        stringResource(R.string.chance_label),
                        color = colors.primary,
                        style = MaterialTheme.typography.labelSmall,
                        letterSpacing = 2.sp
                    )
                    Text(
                        stringResource(R.string.screen_headline),
                        style = MaterialTheme.typography.headlineLarge
                    )
                }
                CoinSection(viewModel, coinSize)
                Button(
                    onClick = viewModel::flipCoin,
                    enabled = !viewModel.isFlipping,
                    shape = RoundedCornerShape(20.dp),
                    modifier = Modifier.fillMaxWidth().heightIn(min = 60.dp),
                    contentPadding = PaddingValues(18.dp)
                ) {
                    Text(
                        stringResource(
                            if (viewModel.isFlipping) R.string.flipping else R.string.flip_coin
                        ),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                }
                StatsSection(viewModel)
                Text(
                    stringResource(R.string.fair_chance),
                    color = colors.onSurfaceVariant,
                    style = MaterialTheme.typography.labelMedium
                )
            }
        }
    }
}

@Composable
private fun CoinSection(viewModel: CoinFlipViewModel, coinSize: Dp) {
    val progress = remember { Animatable(0f) }
    var startingSide by remember { mutableStateOf(viewModel.coinSide) }
    val context = LocalContext.current
    val haptics = LocalHapticFeedback.current
    val player = remember(context) {
        MediaPlayer.create(context, R.raw.coin_flip).also {
            if (it == null) Log.w("CoinFlipScreen", "Coin flip audio could not be loaded")
        }
    }
    DisposableEffect(player) {
        onDispose { player?.release() }
    }
    LaunchedEffect(viewModel.isFlipping) {
        if (viewModel.isFlipping) {
            startingSide = viewModel.coinSide
            progress.snapTo(0f)
            player?.seekTo(0)
            player?.start()
            progress.animateTo(1f, tween(1400, easing = FastOutSlowInEasing))
            viewModel.onFlipAnimationEnd()
            haptics.performHapticFeedback(HapticFeedbackType.LongPress)
        }
    }
    val turns = if (startingSide == viewModel.landingSide) 1800f else 1980f
    val rotation = progress.value * turns
    val backVisible = (rotation % 360f) in 90f..270f
    val visibleSide = if (!viewModel.isFlipping) viewModel.coinSide
        else if (backVisible) {
            if (startingSide == CoinSide.HEADS) CoinSide.TAILS else CoinSide.HEADS
        } else startingSide
    val lift = if (viewModel.isFlipping) sin(progress.value * PI).toFloat() else 0f
    val shadowColor = MaterialTheme.colorScheme.onBackground
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(coinSize + 48.dp)
                .drawBehind {
                    val width = size.width * (0.46f - lift * 0.12f)
                    drawOval(
                        brush = Brush.radialGradient(
                            listOf(shadowColor.copy(alpha = 0.18f - lift * 0.08f), Color.Transparent),
                            center = Offset(size.width / 2, size.height - 16.dp.toPx()),
                            radius = width / 2
                        ),
                        topLeft = Offset((size.width - width) / 2, size.height - 28.dp.toPx()),
                        size = Size(width, 24.dp.toPx())
                    )
                },
            contentAlignment = Alignment.Center
        ) {
            GoldCoin(
                side = visibleSide,
                modifier = Modifier
                    .size(coinSize)
                    .graphicsLayer {
                        translationY = -lift * 28.dp.toPx()
                        rotationX = if (viewModel.isFlipping) rotation else 0f
                        if (viewModel.isFlipping && backVisible) rotationX += 180f
                        rotationZ = if (viewModel.isFlipping) lift * -12f else -8f
                        scaleX = 1f + lift * 0.06f
                        scaleY = 1f + lift * 0.06f
                        cameraDistance = 14 * density
                    }
            )
        }
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(4.dp),
            modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite }
        ) {
            Text(
                text = stringResource(
                    when {
                        viewModel.isFlipping -> R.string.in_the_air
                        viewModel.flipCount == 0 -> R.string.ready_to_flip
                        viewModel.coinSide == CoinSide.HEADS -> R.string.heads
                        else -> R.string.tails
                    }
                ),
                style = MaterialTheme.typography.headlineMedium
            )
            Text(
                stringResource(
                    if (viewModel.isFlipping) R.string.chance_working else R.string.coin_hint
                ),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun StatsSection(viewModel: CoinFlipViewModel) {
    val colors = MaterialTheme.colorScheme
    Card(
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = colors.surface),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(
                Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    stringResource(R.string.this_session),
                    style = MaterialTheme.typography.titleSmall
                )
                TextButton(
                    onClick = viewModel::resetStats,
                    enabled = !viewModel.isFlipping && viewModel.flipCount > 0,
                    contentPadding = PaddingValues(horizontal = 12.dp)
                ) {
                    Text(stringResource(R.string.reset_stats))
                }
            }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                StatItem(stringResource(R.string.total_flips), viewModel.flipCount)
                StatItem(stringResource(R.string.heads), viewModel.headsCount)
                StatItem(stringResource(R.string.tails), viewModel.tailsCount)
            }
            val headsFraction = if (viewModel.flipCount == 0) 0.5f
                else viewModel.headsCount.toFloat() / viewModel.flipCount
            BoxWithConstraints(
                Modifier.fillMaxWidth().height(5.dp)
                    .background(colors.surfaceVariant, RoundedCornerShape(3.dp))
            ) {
                Box(
                    Modifier.width(maxWidth * headsFraction).fillMaxHeight()
                        .background(colors.primary, RoundedCornerShape(3.dp))
                )
            }
        }
    }
}

@Composable
private fun StatItem(label: String, value: Int) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(value.toString(), style = MaterialTheme.typography.headlineMedium)
        Text(
            label,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
