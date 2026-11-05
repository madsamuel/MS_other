package com.seattledevcamp.coinflipper

import android.graphics.Paint
import android.graphics.Typeface
import androidx.compose.foundation.Canvas
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.sin

private val GoldDark = Color(0xFF795019)
private val GoldLight = Color(0xFFFFEDAD)

@Composable
fun GoldCoin(side: CoinSide, modifier: Modifier = Modifier) {
    val label = stringResource(if (side == CoinSide.HEADS) R.string.heads else R.string.tails)
    val inscription = stringResource(R.string.coin_inscription)
    Canvas(modifier.semantics { contentDescription = label }) {
        val scale = size.minDimension / 280f
        withTransform({
            translate((size.width - 280 * scale) / 2, (size.height - 280 * scale) / 2)
            scale(scale, scale, Offset.Zero)
        }) {
            drawCircle(GoldDark, 136f, Offset(140f, 144f))
            drawCircle(
                Brush.linearGradient(
                    listOf(GoldLight, Color(0xFFD8A743), GoldDark, Color(0xFFE4BC61)),
                    Offset(25f, 0f), Offset(240f, 280f)
                ),
                136f, Offset(140f, 140f)
            )
            repeat(120) { index ->
                rotate(index * 3f, Offset(140f, 140f)) {
                    drawLine(GoldDark.copy(alpha = 0.7f), Offset(140f, 6f), Offset(140f, 14f), 1.4f)
                    drawLine(GoldLight.copy(alpha = 0.8f), Offset(142f, 6f), Offset(142f, 13f), 0.8f)
                }
            }
            drawCircle(GoldLight, 125f, Offset(140f, 140f), style = Stroke(2f))
            drawCircle(GoldDark, 121f, Offset(140f, 140f), style = Stroke(1.5f))
            drawCircle(
                Brush.linearGradient(
                    listOf(Color(0xFFF5D67E), Color(0xFFCC9B37), Color(0xFFF4D88C)),
                    Offset(45f, 40f), Offset(240f, 260f)
                ),
                118f, Offset(140f, 140f)
            )
            // Fine concentric machining marks keep the face metallic at every display size.
            repeat(34) { index ->
                drawCircle(
                    GoldDark.copy(alpha = 0.045f), 35f + index * 2.4f,
                    Offset(140f, 140f), style = Stroke(0.5f)
                )
            }
            repeat(60) { index ->
                val angle = index * PI / 30
                drawCircle(
                    GoldDark.copy(alpha = 0.65f), 1.15f,
                    Offset(140f + cos(angle).toFloat() * 111, 140f + sin(angle).toFloat() * 111)
                )
            }
            coinLettering(label.uppercase(java.util.Locale.ROOT), 65f, 17f)
            coinLettering(inscription, 223f, 9f)
            if (side == CoinSide.HEADS) drawPortrait() else drawCompass()
            drawCircle(
                Brush.radialGradient(
                    listOf(Color.White.copy(alpha = 0.24f), Color.Transparent),
                    Offset(75f, 65f), 200f
                ),
                118f, Offset(140f, 140f)
            )
        }
    }
}

private fun DrawScope.coinLettering(text: String, y: Float, textSize: Float) {
    val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        this.textSize = textSize
        textAlign = Paint.Align.CENTER
        typeface = Typeface.create("serif", Typeface.BOLD)
        textScaleX = 1.12f
    }
    paint.color = android.graphics.Color.rgb(255, 232, 161)
    drawContext.canvas.nativeCanvas.drawText(text, 140.6f, y + 0.9f, paint)
    paint.color = android.graphics.Color.rgb(116, 77, 23)
    drawContext.canvas.nativeCanvas.drawText(text, 140f, y, paint)
}

private fun DrawScope.drawPortrait() {
    val portrait = Path().apply {
        moveTo(99f, 194f)
        cubicTo(106f, 180f, 127f, 183f, 130f, 169f)
        lineTo(130f, 160f)
        cubicTo(115f, 153f, 110f, 138f, 111f, 120f)
        cubicTo(102f, 116f, 105f, 96f, 119f, 90f)
        cubicTo(130f, 78f, 156f, 80f, 168f, 93f)
        cubicTo(177f, 100f, 177f, 111f, 173f, 122f)
        lineTo(183f, 137f)
        quadraticTo(185f, 141f, 175f, 142f)
        lineTo(174f, 151f)
        quadraticTo(176f, 160f, 158f, 161f)
        lineTo(156f, 174f)
        quadraticTo(158f, 181f, 177f, 187f)
        lineTo(184f, 196f)
        close()
    }
    translate(1.4f, 2f) { drawPath(portrait, GoldLight) }
    drawPath(
        portrait,
        Brush.linearGradient(
            listOf(GoldDark, Color(0xFFE7BD60), Color(0xFFAA7828)),
            Offset(110f, 95f), Offset(180f, 185f)
        )
    )
    drawPath(portrait, GoldDark.copy(alpha = 0.7f), style = Stroke(1f))
    repeat(5) { index ->
        val hair = Path().apply {
            moveTo(116f + index * 6f, 101f)
            quadraticTo(122f + index * 6f, 87f, 137f + index * 6f, 97f)
        }
        drawPath(hair, GoldLight.copy(alpha = 0.7f), style = Stroke(1.6f))
    }
    drawLine(GoldDark, Offset(163f, 119f), Offset(170f, 120f), 1.8f)
    drawLine(GoldLight, Offset(138f, 166f), Offset(149f, 172f), 1.5f)
    drawLaurels()
}

private fun DrawScope.drawCompass() {
    val star = Path().apply {
        repeat(16) { index ->
            val angle = index * PI / 8 - PI / 2
            val radius = if (index % 2 == 0) {
                if (index % 4 == 0) 53f else 37f
            } else 14f
            val x = 140 + cos(angle).toFloat() * radius
            val y = 139 + sin(angle).toFloat() * radius
            if (index == 0) moveTo(x, y) else lineTo(x, y)
        }
        close()
    }
    drawCircle(GoldDark, 44f, Offset(140f, 139f), style = Stroke(1f))
    drawCircle(GoldLight, 46f, Offset(140f, 140f), style = Stroke(1f))
    translate(1f, 2f) { drawPath(star, GoldLight) }
    drawPath(
        star,
        Brush.linearGradient(listOf(GoldLight, GoldDark), Offset(110f, 85f), Offset(170f, 190f))
    )
    drawPath(star, GoldDark, style = Stroke(1f))
    drawCircle(GoldDark, 7f, Offset(140f, 139f))
    drawCircle(GoldLight, 3f, Offset(139f, 138f))
    drawLaurels()
}

private fun DrawScope.drawLaurels() {
    for (direction in listOf(-1f, 1f)) {
        repeat(7) { index ->
            val angle = (25 + index * 11) * PI / 180
            val x = 140 + direction * cos(angle).toFloat() * 84f
            val y = 134 + sin(angle).toFloat() * 70f
            rotate(direction * (index * 9f - 35), Offset(x, y)) {
                drawOval(
                    GoldDark.copy(alpha = 0.7f),
                    Offset(x - 3, y - 7), androidx.compose.ui.geometry.Size(5f, 12f)
                )
                drawLine(GoldLight, Offset(x, y - 5), Offset(x, y + 3), 0.8f)
            }
        }
    }
}
