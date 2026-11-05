package com.seattledevcamp.coinflipper

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class CoinFlipViewModelTest {
    @Test
    fun resultIsNotRecordedUntilLanding() {
        val model = CoinFlipViewModel()
        model.flipCoin()
        val landingSide = model.landingSide

        assertTrue(model.isFlipping)
        assertEquals(0, model.flipCount)
        model.flipCoin()
        assertEquals(landingSide, model.landingSide)

        model.onFlipAnimationEnd()
        assertFalse(model.isFlipping)
        assertEquals(landingSide, model.coinSide)
        assertEquals(1, model.flipCount)
        assertEquals(if (landingSide == CoinSide.HEADS) 1 else 0, model.headsCount)
        assertEquals(if (landingSide == CoinSide.TAILS) 1 else 0, model.tailsCount)
    }

    @Test
    fun everyLandingCountsExactlyOnceAndResetClearsStatistics() {
        val model = CoinFlipViewModel()
        repeat(30) {
            model.flipCoin()
            val landingSide = model.landingSide
            model.onFlipAnimationEnd()
            assertEquals(landingSide, model.coinSide)
        }
        assertEquals(30, model.flipCount)
        assertEquals(model.flipCount, model.headsCount + model.tailsCount)
        model.resetStats()
        assertEquals(0, model.flipCount)
        assertEquals(0, model.headsCount)
        assertEquals(0, model.tailsCount)
        assertFalse(model.isFlipping)
    }
}
