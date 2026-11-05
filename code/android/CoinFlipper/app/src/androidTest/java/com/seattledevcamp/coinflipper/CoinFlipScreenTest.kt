package com.seattledevcamp.coinflipper

import androidx.compose.material3.Surface
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertIsEnabled
import androidx.compose.ui.test.assertIsNotEnabled
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class CoinFlipScreenTest {
    @get:Rule
    val compose = createComposeRule()

    @Test
    fun lightThemeFlipLandsAndStatisticsCanBeReset() {
        verifyFlipAndReset(darkTheme = false)
    }

    @Test
    fun darkThemeFlipLandsAndStatisticsCanBeReset() {
        verifyFlipAndReset(darkTheme = true)
    }

    private fun verifyFlipAndReset(darkTheme: Boolean) {
        val model = CoinFlipViewModel()
        compose.setContent {
            CoinFlipTheme(darkTheme = darkTheme) {
                Surface { CoinFlipScreen(model) }
            }
        }
        compose.onNodeWithText("Ready to flip?").assertIsDisplayed()
        compose.onNodeWithText("Reset stats").performScrollTo().assertIsNotEnabled()
        compose.mainClock.autoAdvance = false
        compose.onNodeWithText("Flip coin").performScrollTo().performClick()
        compose.mainClock.advanceTimeBy(100)
        compose.onNodeWithText("Flipping...").assertIsNotEnabled()
        compose.mainClock.advanceTimeBy(1700)
        compose.mainClock.autoAdvance = true
        compose.waitForIdle()
        compose.runOnIdle {
            assertEquals(1, model.flipCount)
            assertEquals(model.landingSide, model.coinSide)
            assertEquals(1, model.headsCount + model.tailsCount)
        }
        compose.onNodeWithText("Flip coin").assertIsEnabled()
        compose.onNodeWithText("Reset stats").performScrollTo().performClick()
        compose.runOnIdle {
            assertEquals(0, model.flipCount)
            assertEquals(0, model.headsCount)
            assertEquals(0, model.tailsCount)
        }
        compose.onNodeWithText("Reset stats").assertIsNotEnabled()
    }
}
