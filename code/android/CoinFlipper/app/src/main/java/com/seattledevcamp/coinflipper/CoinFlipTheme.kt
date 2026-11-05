package com.seattledevcamp.coinflipper

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.material3.Typography
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

private val LightColors = lightColorScheme(
    primary = Color(0xFF79551B),
    onPrimary = Color.White,
    secondary = Color(0xFF79551B),
    background = Color(0xFFF8F5EE),
    onBackground = Color(0xFF282820),
    surface = Color(0xFFFFFCF6),
    onSurface = Color(0xFF282820),
    surfaceVariant = Color(0xFFEEE8DC),
    onSurfaceVariant = Color(0xFF6D685C),
    outlineVariant = Color(0xFFDED6C6)
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFFE6C47E),
    onPrimary = Color(0xFF30230C),
    secondary = Color(0xFFE6C47E),
    background = Color(0xFF171917),
    onBackground = Color(0xFFF6F0E2),
    surface = Color(0xFF222521),
    onSurface = Color(0xFFF6F0E2),
    surfaceVariant = Color(0xFF30342E),
    onSurfaceVariant = Color(0xFFBDBDAF),
    outlineVariant = Color(0xFF41463C)
)

private val CoinTypography = Typography(
    headlineLarge = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Normal,
        fontSize = 36.sp,
        lineHeight = 42.sp,
        letterSpacing = (-1).sp
    ),
    headlineMedium = TextStyle(
        fontFamily = FontFamily.Serif,
        fontSize = 30.sp,
        lineHeight = 36.sp
    )
)

@Composable
fun CoinFlipTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colors = if (darkTheme) {
        DarkColors
    } else {
        LightColors
    }

    MaterialTheme(
        colorScheme = colors,
        typography = CoinTypography,
        content = content
    )
}
