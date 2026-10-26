package com.madsamuel.youtube3x

import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.MutableContextWrapper
import android.content.pm.ServiceInfo
import android.media.MediaMetadata
import android.media.session.MediaSession
import android.media.session.PlaybackState
import android.net.Uri
import android.net.http.SslError
import android.os.Binder
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.PowerManager
import android.view.ViewGroup
import android.webkit.CookieManager
import android.webkit.SslErrorHandler
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.webkit.WebViewCompat
import androidx.webkit.WebViewFeature
import org.json.JSONObject
import org.json.JSONTokener
import java.io.ByteArrayInputStream

class PlaybackService : Service() {
    interface Listener {
        fun onStatus(text: String, isWarning: Boolean)
        fun onProgress(progress: Int)
        fun onTitle(title: String)
        fun onLocation(url: String)
        fun onPlaybackChanged(playing: Boolean)
        fun onExternalLink(uri: Uri)
        fun onStopped()
    }

    inner class LocalBinder : Binder() {
        val service: PlaybackService get() = this@PlaybackService
    }

    lateinit var webView: WebView
        private set
    lateinit var webContext: MutableContextWrapper
        private set
    var listener: Listener? = null
    var requestedRate = 3
        private set
    @Volatile
    var adBlockingEnabled = true
        private set
    var titleText = ""
        private set
    var statusText = ""
        private set
    var statusIsWarning = false
        private set
    private lateinit var script: String
    private lateinit var mediaSession: MediaSession
    private lateinit var wakeLock: PowerManager.WakeLock
    var playing = false
        private set
    private var pageFailed = false
    private var stopped = false
    private var commandPending = false
    private var foreground = false
    private var positionMs = 0L
    private var metadataDurationMs = -1L
    private var generation = 0
    private val handler = Handler(Looper.getMainLooper())
    private val poll = object : Runnable {
        override fun run() {
            updatePlayback()
            handler.postDelayed(this, if (playing) 1500 else 4000)
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate() {
        super.onCreate()
        requestedRate = if (getSharedPreferences("playback", MODE_PRIVATE).getInt("speed", 3) == 1) 1 else 3
        adBlockingEnabled = getSharedPreferences("playback", MODE_PRIVATE).getBoolean("ad_blocking", true)
        val background = asset("background-playback.js")
        script = background + "\n" + asset("ad-block.js") + "\n" + asset("playback-speed.js")
        webContext = MutableContextWrapper(applicationContext)
        webView = PlaybackWebView(webContext)
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            mediaPlaybackRequiresUserGesture = true
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            allowFileAccess = false
            allowContentAccess = false
        }
        if (WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT)) {
            WebViewCompat.addDocumentStartJavaScript(
                webView, background,
                setOf("https://youtube.com", "https://www.youtube.com", "https://m.youtube.com")
            )
        }
        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, false)
        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {
                if (!request.isForMainFrame &&
                    AdBlockRules.shouldBlock(request.url.toString(), adBlockingEnabled)) {
                    return WebResourceResponse(
                        "text/plain", "UTF-8", 200, "OK", mapOf("Cache-Control" to "no-store"),
                        ByteArrayInputStream(ByteArray(0))
                    )
                }
                return super.shouldInterceptRequest(view, request)
            }

            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val url = request.url.toString()
                val uri = request.url
                val consent = uri.scheme == "https" && uri.host == "consent.youtube.com" &&
                    uri.userInfo == null && (uri.port == -1 || uri.port == 443)
                if (YouTubeNavigation.isYouTubeUrl(url) || consent) return false
                if (request.isForMainFrame && request.hasGesture() && uri.scheme == "https") {
                    listener?.onExternalLink(uri)
                }
                return true
            }

            override fun onPageStarted(view: WebView, url: String?, favicon: android.graphics.Bitmap?) {
                pageFailed = false
                generation++
                setPlaying(false)
                titleText = ""
                positionMs = 0L
                metadataDurationMs = -1L
                mediaSession.setMetadata(null)
                listener?.onTitle("")
                listener?.onLocation(url.orEmpty())
                report(getString(R.string.waiting, requestedRate.toString()), isWarning = false)
            }

            override fun onPageFinished(view: WebView, url: String?) {
                updatePlayback()
                updateNavigation()
            }

            override fun doUpdateVisitedHistory(view: WebView, url: String?, isReload: Boolean) {
                updateNavigation()
            }

            override fun onReceivedError(view: WebView, request: WebResourceRequest, error: WebResourceError) {
                if (request.isForMainFrame) pageError()
            }

            override fun onReceivedHttpError(view: WebView, request: WebResourceRequest, response: WebResourceResponse) {
                if (request.isForMainFrame) pageError()
            }

            override fun onReceivedSslError(view: WebView, handler: SslErrorHandler, error: SslError) {
                handler.cancel()
                pageError()
            }
        }
        resetChromeClient()
        wakeLock = getSystemService(PowerManager::class.java)
            .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "$packageName:playback")
        wakeLock.setReferenceCounted(false)
        mediaSession = MediaSession(this, "YouTube3x").apply {
            setCallback(object : MediaSession.Callback() {
                override fun onPlay() = setPlayback(true)
                override fun onPause() = setPlayback(false)
                override fun onStop() = stopPlayback()
            }, handler)
            isActive = true
        }
        getSystemService(NotificationManager::class.java).createNotificationChannel(
            NotificationChannel(CHANNEL, getString(R.string.playback_channel), NotificationManager.IMPORTANCE_LOW)
        )
        publishState()
        handler.post(poll)
    }

    private fun asset(name: String) = assets.open(name).bufferedReader().use { it.readText() }

    fun resetChromeClient() {
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView, newProgress: Int) {
                listener?.onProgress(newProgress)
            }
        }
    }

    fun selectSpeed(rate: Int) {
        require(rate == 1 || rate == 3)
        requestedRate = rate
        getSharedPreferences("playback", MODE_PRIVATE).edit().putInt("speed", rate).apply()
        publishState()
        updatePlayback()
    }

    fun setAdBlockingEnabled(enabled: Boolean) {
        adBlockingEnabled = enabled
        getSharedPreferences("playback", MODE_PRIVATE).edit().putBoolean("ad_blocking", enabled).apply()
        updatePlayback()
    }

    private fun updateNavigation() {
        listener?.onLocation(webView.url.orEmpty())
    }

    private fun pageError() {
        pageFailed = true
        setPlaying(false)
        report(getString(R.string.page_error))
    }

    private fun report(text: String, isWarning: Boolean = true) {
        if (statusText == text && statusIsWarning == isWarning) return
        statusText = text
        statusIsWarning = isWarning
        listener?.onStatus(text, isWarning)
    }

    private fun updatePlayback() {
        if (stopped || commandPending || pageFailed) return
        val url = webView.url ?: return
        if (!YouTubeNavigation.isYouTubeUrl(url)) {
            setPlaying(false)
            report(getString(R.string.external_page))
            return
        }
        val rate = requestedRate
        val currentGeneration = generation
        val configuredScript = script
            .replace("__AD_BLOCK_ENABLED__", adBlockingEnabled.toString())
            .replace("__REQUESTED_RATE__", rate.toString())
        webView.evaluateJavascript(configuredScript) { result ->
            if (stopped || commandPending || pageFailed || generation != currentGeneration ||
                webView.url != url || requestedRate != rate) return@evaluateJavascript
            val json = JSONTokener(result).nextValue()
            if (json !is String) {
                report(getString(R.string.speed_error, getString(R.string.script_unavailable)))
                return@evaluateJavascript
            }
            val playback = JSONObject(json)
            val title = playback.optString("title").takeIf(String::isNotBlank).orEmpty()
            val titleChanged = title != titleText
            if (titleChanged) {
                titleText = title
                listener?.onTitle(title)
            }
            val durationMs = (playback.optDouble("duration", 0.0) * 1000).toLong().coerceAtLeast(0L)
            positionMs = (playback.optDouble("position", 0.0) * 1000).toLong().coerceAtLeast(0L)
            if (titleChanged || durationMs != metadataDurationMs) {
                metadataDurationMs = durationMs
                mediaSession.setMetadata(MediaMetadata.Builder()
                    .putString(MediaMetadata.METADATA_KEY_TITLE, title.ifBlank { getString(R.string.app_name) })
                    .putString(MediaMetadata.METADATA_KEY_DISPLAY_TITLE, title.ifBlank { getString(R.string.app_name) })
                    .putLong(MediaMetadata.METADATA_KEY_DURATION, durationMs)
                    .build())
                if (titleChanged && foreground) {
                    getSystemService(NotificationManager::class.java).notify(NOTIFICATION, notification())
                }
            }
            setPlaying(playback.getBoolean("playing"))
            publishState()
            when {
                !playback.isNull("commandError") ->
                    report(getString(R.string.playback_command_error, playback.getString("commandError")))
                !playback.isNull("fullscreenError") ->
                    report(getString(R.string.fullscreen_error, playback.getString("fullscreenError")))
                !playback.isNull("adError") -> report(getString(R.string.ad_block_error, playback.getString("adError")))
                !playback.isNull("error") -> report(getString(R.string.speed_error, playback.getString("error")))
                !playback.getBoolean("found") -> report(getString(R.string.waiting, rate.toString()), isWarning = false)
                playback.getDouble("actual") == rate.toDouble() ->
                    report(getString(R.string.speed_status, rate.toString()), isWarning = false)
                else -> report(getString(R.string.speed_unavailable, rate.toString(), playback.get("actual").toString()))
            }
        }
    }

    fun enterVideoFullscreen() {
        // loadUrl preserves the native button's user gesture for the fullscreen request.
        webView.loadUrl("javascript:" + """
            (function() {
                window.youtube3xFullscreenError = null;
                const videos = Array.from(document.querySelectorAll('video'));
                const video = videos.find(v => !v.paused && v.readyState > 0) ||
                    videos.find(v => v.readyState > 0);
                if (!video) {
                    window.youtube3xFullscreenError = ${JSONObject.quote(getString(R.string.fullscreen_no_video))};
                    return;
                }
                try {
                    video.requestFullscreen().catch(error => {
                        window.youtube3xFullscreenError = error.message || String(error);
                    });
                } catch (error) {
                    window.youtube3xFullscreenError = error.message || String(error);
                }
            })();
        """.trimIndent())
    }

    private fun setPlaying(value: Boolean) {
        if (value) {
            if (!wakeLock.isHeld) wakeLock.acquire()
            if (!foreground) {
                if (Build.VERSION.SDK_INT >= 29) {
                    startForeground(NOTIFICATION, notification(), ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK)
                } else startForeground(NOTIFICATION, notification())
                foreground = true
            }
        } else {
            if (wakeLock.isHeld) wakeLock.release()
        }
        if (playing == value) return
        playing = value
        listener?.onPlaybackChanged(playing)
        publishState()
        if (playing) {
            getSystemService(NotificationManager::class.java).notify(NOTIFICATION, notification())
        } else if (foreground) {
            stopForeground(STOP_FOREGROUND_REMOVE)
            foreground = false
        }
    }

    private fun setPlayback(play: Boolean) {
        if (stopped) return
        commandPending = true
        generation++
        val command = if (play) """
            window.youtube3xPlayError = null;
            (async function() {
                const video = Array.from(document.querySelectorAll('video')).find(v => v.readyState > 0);
                if (!video) return 'No video selected';
                try { await video.play(); return null; }
                catch (error) { return error.message || String(error); }
            })().then(error => { window.youtube3xPlayError = error; });
        """.trimIndent() else "document.querySelectorAll('video').forEach(video => video.pause());"
        // evaluateJavascript does not await promises; the poll reads any play rejection.
        webView.evaluateJavascript(command, null)
        if (!play) setPlaying(false)
        handler.postDelayed({
            commandPending = false
            if (!stopped) {
                updatePlayback()
            }
        }, 250)
    }

    private fun publishState() {
        mediaSession.setPlaybackState(PlaybackState.Builder()
            .setActions(PlaybackState.ACTION_PLAY or PlaybackState.ACTION_PAUSE or
                PlaybackState.ACTION_PLAY_PAUSE or PlaybackState.ACTION_STOP)
            .setState(if (playing) PlaybackState.STATE_PLAYING else PlaybackState.STATE_PAUSED,
                positionMs, if (playing) requestedRate.toFloat() else 0f)
            .build())
    }

    private fun notification(): Notification {
        val open = PendingIntent.getActivity(this, 0,
            Intent(this, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        fun action(name: String, id: Int) = PendingIntent.getService(this, id,
            Intent(this, PlaybackService::class.java).setAction(name),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        return Notification.Builder(this, CHANNEL)
            .setSmallIcon(R.drawable.ic_launcher)
            .setContentTitle(titleText.ifBlank { getString(R.string.app_name) })
            .setContentText(getString(R.string.playing_at_speed, requestedRate.toString()))
            .setContentIntent(open)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setVisibility(Notification.VISIBILITY_PUBLIC)
            .addAction(Notification.Action.Builder(
                null, getString(if (playing) R.string.pause else R.string.play),
                action(if (playing) PAUSE else PLAY, 1)).build())
            .addAction(Notification.Action.Builder(null, getString(R.string.stop), action(STOP, 2)).build())
            .setStyle(Notification.MediaStyle().setMediaSession(mediaSession.sessionToken)
                .setShowActionsInCompactView(0, 1))
            .build()
    }

    private fun stopPlayback() {
        if (stopped) return
        stopped = true
        handler.removeCallbacksAndMessages(null)
        webView.evaluateJavascript("document.querySelectorAll('video').forEach(video => video.pause());", null)
        setPlaying(false)
        listener?.onStopped()
        listener = null
        if (foreground) {
            stopForeground(STOP_FOREGROUND_REMOVE)
            foreground = false
        }
        stopSelf()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            PLAY -> setPlayback(true)
            PAUSE -> setPlayback(false)
            STOP -> stopPlayback()
        }
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent): IBinder = LocalBinder()

    override fun onTaskRemoved(rootIntent: Intent?) {
        stopPlayback()
        super.onTaskRemoved(rootIntent)
    }

    override fun onDestroy() {
        stopped = true
        handler.removeCallbacksAndMessages(null)
        listener = null
        if (wakeLock.isHeld) wakeLock.release()
        mediaSession.release()
        (webView.parent as? ViewGroup)?.removeView(webView)
        webView.stopLoading()
        webView.destroy()
        super.onDestroy()
    }

    companion object {
        private const val CHANNEL = "background_playback"
        private const val NOTIFICATION = 1
        private const val PLAY = "play"
        private const val PAUSE = "pause"
        private const val STOP = "stop"
    }
}
