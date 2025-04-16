package com.seattledevcamp.coinflipper

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import kotlin.random.Random

class CoinFlipViewModel : ViewModel() {
    var coinSide by mutableStateOf(CoinSide.HEADS)
        private set

    var isFlipping by mutableStateOf(false)
        private set

    var flipCount by mutableStateOf(0)
        private set

    var headsCount by mutableStateOf(0)
        private set

    var tailsCount by mutableStateOf(0)
        private set

    fun flipCoin() {
        if (!isFlipping) {
            isFlipping = true
            // The actual result will be set after the animation completes
        }
    }

    fun onFlipAnimationEnd() {
        // Determine the result
        coinSide = if (Random.nextBoolean()) CoinSide.HEADS else CoinSide.TAILS
        isFlipping = false
        flipCount++

        if (coinSide == CoinSide.HEADS) {
            headsCount++
        } else {
            tailsCount++
        }
    }

    fun resetStats() {
        flipCount = 0
        headsCount = 0
        tailsCount = 0
    }
}

enum class CoinSide {
    HEADS, TAILS
}
