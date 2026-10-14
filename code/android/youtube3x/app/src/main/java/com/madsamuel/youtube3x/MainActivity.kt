package com.madsamuel.youtube3x

import android.annotation.SuppressLint
import android.content.ActivityNotFoundException
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.net.http.SslError
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.WindowManager
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputMethodManager
import android.webkit.CookieManager
import android.webkit.SslErrorHandler
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import org.json.JSONObject
import org.json.JSONTokener

class MainActivity : ComponentActivity() {
    private lateinit var webView: WebView
    private lateinit var status: TextView
    private lateinit var address: EditText
    private lateinit var fullscreen: FrameLayout
    private lateinit var browserContent: View
    private lateinit var speedScript: String
    private var customViewCallback: WebChromeClient.CustomViewCallback? = null
    private var requestedRate = 3
    private var pageFailed = false
    private var resumed = false
    private val handler = Handler(Looper.getMainLooper())
    private val poll = object : Runnable {
        override fun run() {
            updatePlaybackSpeed()
            handler.postDelayed(this, 1000)
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        setContentView(R.layout.activity_main)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.root)) { view, insets ->
            val bars = insets.getInsets(
                WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.ime()
            )
            view.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            insets
        }
        webView = findViewById(R.id.web_view)
        status = findViewById(R.id.status)
        address = findViewById(R.id.address)
        fullscreen = findViewById(R.id.fullscreen_container)
        browserContent = findViewById(R.id.browser_content)
        speedScript = assets.open("playback-speed.js").bufferedReader().use { it.readText() }
        val preferences = getSharedPreferences("playback", MODE_PRIVATE)
        requestedRate = if (preferences.getInt("speed", 3) == 1) 1 else 3
        updateSpeedButtons()
        showWaiting()

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            mediaPlaybackRequiresUserGesture = true
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            allowFileAccess = false
            allowContentAccess = false
        }
        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, false)
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val url = request.url.toString()
                if (YouTubeNavigation.isYouTubeUrl(url) || isConsentPage(url)) return false
                if (request.isForMainFrame && request.hasGesture() &&
                    request.url.scheme == "https"
                ) openExternal(request.url)
                return true
            }

            override fun onPageStarted(view: WebView, url: String?, favicon: Bitmap?) {
                pageFailed = false
                showWaiting()
            }

            override fun onPageFinished(view: WebView, url: String?) {
                if (resumed) updatePlaybackSpeed()
            }

            override fun onReceivedError(
                view: WebView, request: WebResourceRequest, error: WebResourceError
            ) {
                if (request.isForMainFrame) {
                    pageFailed = true
                    status.setText(R.string.page_error)
                }
            }

            override fun onReceivedHttpError(
                view: WebView, request: WebResourceRequest, response: WebResourceResponse
            ) {
                if (request.isForMainFrame) {
                    pageFailed = true
                    status.setText(R.string.page_error)
                }
            }

            override fun onReceivedSslError(view: WebView, handler: SslErrorHandler, error: SslError) {
                handler.cancel()
                pageFailed = true
                status.setText(R.string.page_error)
            }
        }
        val progress = findViewById<ProgressBar>(R.id.progress)
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView, newProgress: Int) {
                progress.progress = newProgress
                progress.visibility = if (newProgress == 100) View.GONE else View.VISIBLE
            }

            override fun onShowCustomView(view: View, callback: CustomViewCallback) {
                if (customViewCallback != null) {
                    callback.onCustomViewHidden()
                    return
                }
                customViewCallback = callback
                fullscreen.addView(view)
                fullscreen.visibility = View.VISIBLE
                browserContent.visibility = View.GONE
                window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                WindowInsetsControllerCompat(window, fullscreen).apply {
                    systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
                    hide(WindowInsetsCompat.Type.systemBars())
                }
            }

            override fun onHideCustomView() = exitFullscreen()
        }
        findViewById<Button>(R.id.home).setOnClickListener { webView.loadUrl(YouTubeNavigation.HOME) }
        findViewById<Button>(R.id.reload).setOnClickListener { webView.reload() }
        findViewById<Button>(R.id.normal_speed).setOnClickListener { selectSpeed(1) }
        findViewById<Button>(R.id.triple_speed).setOnClickListener { selectSpeed(3) }
        findViewById<Button>(R.id.go).setOnClickListener { navigate() }
        address.setOnEditorActionListener { _, action, _ ->
            if (action == EditorInfo.IME_ACTION_GO) {
                navigate()
                true
            } else false
        }
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                when {
                    customViewCallback != null -> exitFullscreen()
                    webView.canGoBack() -> webView.goBack()
                    else -> {
                        isEnabled = false
                        onBackPressedDispatcher.onBackPressed()
                        isEnabled = true
                    }
                }
            }
        })
        if (savedInstanceState == null || webView.restoreState(savedInstanceState) == null) {
            webView.loadUrl(sharedVideo(intent) ?: YouTubeNavigation.HOME)
        }
    }

    private fun isConsentPage(url: String): Boolean {
        val uri = Uri.parse(url)
        return uri.scheme == "https" && uri.host == "consent.youtube.com" &&
            uri.userInfo == null && (uri.port == -1 || uri.port == 443)
    }

    private fun sharedVideo(intent: Intent): String? {
        if (intent.action != Intent.ACTION_SEND || intent.type != "text/plain") return null
        val text = intent.getStringExtra(Intent.EXTRA_TEXT).orEmpty()
        val url = Regex("https://[^\\s]+").findAll(text)
            .map { it.value }.firstOrNull { YouTubeNavigation.isYouTubeUrl(it) }
        if (url == null) Toast.makeText(this, R.string.invalid_link, Toast.LENGTH_LONG).show()
        return url
    }

    private fun openExternal(uri: Uri) {
        try {
            startActivity(Intent(Intent.ACTION_VIEW, uri).addCategory(Intent.CATEGORY_BROWSABLE))
        } catch (_: ActivityNotFoundException) {
            Toast.makeText(this, R.string.no_browser, Toast.LENGTH_LONG).show()
        }
    }

    private fun navigate() {
        val destination = YouTubeNavigation.destination(address.text.toString())
        if (destination == null) {
            address.error = getString(R.string.invalid_link)
            return
        }
        address.error = null
        webView.loadUrl(destination)
        address.clearFocus()
        (getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager)
            .hideSoftInputFromWindow(address.windowToken, 0)
    }

    private fun selectSpeed(rate: Int) {
        requestedRate = rate
        getSharedPreferences("playback", MODE_PRIVATE).edit().putInt("speed", rate).apply()
        updateSpeedButtons()
        updatePlaybackSpeed()
    }

    private fun updateSpeedButtons() {
        findViewById<Button>(R.id.normal_speed).isEnabled = requestedRate != 1
        findViewById<Button>(R.id.triple_speed).isEnabled = requestedRate != 3
    }

    private fun showWaiting() {
        status.text = getString(R.string.waiting, requestedRate.toString())
    }

    private fun updatePlaybackSpeed() {
        if (pageFailed) return
        val url = webView.url ?: return
        if (!YouTubeNavigation.isYouTubeUrl(url)) {
            status.setText(R.string.external_page)
            return
        }
        val rate = requestedRate
        webView.evaluateJavascript(speedScript.replace("__REQUESTED_RATE__", rate.toString())) { result ->
            if (!resumed || pageFailed || webView.url != url || requestedRate != rate) return@evaluateJavascript
            val json = JSONTokener(result).nextValue()
            if (json !is String) {
                status.text = getString(R.string.speed_error, getString(R.string.script_unavailable))
                return@evaluateJavascript
            }
            val playback = JSONObject(json)
            when {
                !playback.isNull("error") ->
                    status.text = getString(R.string.speed_error, playback.getString("error"))
                !playback.getBoolean("found") -> showWaiting()
                playback.getDouble("actual") == rate.toDouble() ->
                    status.text = getString(R.string.speed_status, rate.toString())
                else -> status.text = getString(
                    R.string.speed_unavailable, rate.toString(), playback.get("actual").toString()
                )
            }
        }
    }

    private fun exitFullscreen() {
        val callback = customViewCallback ?: return
        customViewCallback = null
        fullscreen.removeAllViews()
        fullscreen.visibility = View.GONE
        browserContent.visibility = View.VISIBLE
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        WindowInsetsControllerCompat(window, fullscreen).show(WindowInsetsCompat.Type.systemBars())
        callback.onCustomViewHidden()
    }

    override fun onResume() {
        super.onResume()
        resumed = true
        webView.onResume()
        handler.post(poll)
    }

    override fun onPause() {
        resumed = false
        handler.removeCallbacks(poll)
        webView.evaluateJavascript(
            "document.querySelectorAll('video').forEach(function(video) { video.pause(); });", null
        )
        webView.onPause()
        CookieManager.getInstance().flush()
        super.onPause()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        webView.saveState(outState)
        super.onSaveInstanceState(outState)
    }

    override fun onDestroy() {
        handler.removeCallbacks(poll)
        exitFullscreen()
        (webView.parent as? android.view.ViewGroup)?.removeView(webView)
        webView.destroy()
        super.onDestroy()
    }
}
