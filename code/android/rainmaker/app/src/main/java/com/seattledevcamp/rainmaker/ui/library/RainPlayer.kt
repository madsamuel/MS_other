package com.seattledevcamp.rainmaker.ui.library

import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer

class RainPlayer(private val exoPlayer: ExoPlayer) {

    fun play(path: String) {
        val mediaItem = MediaItem.fromUri(path)
        exoPlayer.setMediaItem(mediaItem)
        exoPlayer.prepare()
        exoPlayer.playWhenReady = true
    }

    fun stop() {
        exoPlayer.stop()
    }

    fun release() {
        exoPlayer.release()
    }
}

