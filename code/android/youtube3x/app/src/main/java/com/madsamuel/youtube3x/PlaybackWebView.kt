package com.madsamuel.youtube3x

import android.content.Context
import android.webkit.WebView

class PlaybackWebView(context: Context) : WebView(context) {
    override fun onWindowVisibilityChanged(visibility: Int) {
        // Keep Chromium's media renderer active when the activity window is hidden.
        super.onWindowVisibilityChanged(VISIBLE)
    }
}
