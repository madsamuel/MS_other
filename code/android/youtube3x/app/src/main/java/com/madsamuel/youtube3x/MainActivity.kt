package com.madsamuel.youtube3x

import android.content.ActivityNotFoundException
import android.content.ComponentName
import android.content.Intent
import android.content.ServiceConnection
import android.net.Uri
import android.os.Bundle
import android.os.IBinder
import android.os.Parcel
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputMethodManager
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebView
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

class MainActivity : ComponentActivity(), PlaybackService.Listener {
    private lateinit var status: TextView
    private lateinit var pageTitle: TextView
    private lateinit var address: EditText
    private lateinit var fullscreen: FrameLayout
    private lateinit var browserContent: View
    private lateinit var browserParent: ViewGroup
    private var service: PlaybackService? = null
    private var bound = false
    private var savedBrowserState: Bundle? = null
    private var customViewCallback: WebChromeClient.CustomViewCallback? = null
    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName, binder: IBinder) {
            val playback = (binder as PlaybackService.LocalBinder).service
            service = playback
            playback.listener = this@MainActivity
            playback.webContext.baseContext = this@MainActivity
            val webView = playback.webView
            (webView.parent as? ViewGroup)?.removeView(webView)
            browserParent.addView(webView, ViewGroup.LayoutParams.MATCH_PARENT, 0)
            (webView.layoutParams as android.widget.LinearLayout.LayoutParams).weight = 1f
            installChromeClient(webView)
            updateSpeedButtons()
            updateNavigationButtons()
            updateAdBlockButton()
            onStatus(playback.statusText)
            onTitle(playback.titleText)
            onLocation(webView.url.orEmpty())
            if (webView.url == null) {
                if (savedBrowserState == null || webView.restoreState(savedBrowserState!!) == null) {
                    webView.loadUrl(sharedVideo(intent) ?: YouTubeNavigation.HOME)
                }
            } else if (intent.action == Intent.ACTION_SEND) {
                sharedVideo(intent)?.let { webView.loadUrl(it) }
                intent.action = Intent.ACTION_MAIN
            }
        }

        override fun onServiceDisconnected(name: ComponentName) {
            service = null
            finish()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        savedBrowserState = savedInstanceState?.getBundle(BROWSER_STATE)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        setContentView(R.layout.activity_main)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.root)) { view, insets ->
            val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.ime())
            view.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            insets
        }
        status = findViewById(R.id.status)
        pageTitle = findViewById(R.id.page_title)
        address = findViewById(R.id.address)
        fullscreen = findViewById(R.id.fullscreen_container)
        browserContent = findViewById(R.id.browser_content)
        val placeholder = findViewById<WebView>(R.id.web_view)
        browserParent = placeholder.parent as ViewGroup
        browserParent.removeView(placeholder)
        placeholder.destroy()
        findViewById<View>(R.id.home).setOnClickListener { service?.webView?.loadUrl(YouTubeNavigation.HOME) }
        findViewById<View>(R.id.back).setOnClickListener { service?.webView?.goBack() }
        findViewById<View>(R.id.forward).setOnClickListener { service?.webView?.goForward() }
        findViewById<View>(R.id.reload).setOnClickListener { service?.webView?.reload() }
        findViewById<Button>(R.id.normal_speed).setOnClickListener { selectSpeed(1) }
        findViewById<Button>(R.id.triple_speed).setOnClickListener { selectSpeed(3) }
        findViewById<View>(R.id.go).setOnClickListener { navigate() }
        findViewById<Button>(R.id.ad_block).setOnClickListener {
            service?.let {
                it.setAdBlockingEnabled(!it.adBlockingEnabled)
                updateAdBlockButton()
            }
        }
        updateSpeedButtons()
        updateNavigationButtons()
        updateAdBlockButton()
        address.setOnEditorActionListener { _, action, _ ->
            if (action == EditorInfo.IME_ACTION_GO) {
                navigate()
                true
            } else false
        }
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                val webView = service?.webView
                when {
                    customViewCallback != null -> exitFullscreen()
                    webView?.canGoBack() == true -> webView.goBack()
                    else -> moveTaskToBack(true)
                }
            }
        })
    }

    override fun onStart() {
        super.onStart()
        if (!bound) {
            val intent = Intent(this, PlaybackService::class.java)
            startService(intent)
            bound = bindService(intent, connection, BIND_AUTO_CREATE)
        }
    }

    private fun installChromeClient(webView: WebView) {
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView, newProgress: Int) = onProgress(newProgress)

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
    }

    private fun sharedVideo(intent: Intent): String? {
        if (intent.action != Intent.ACTION_SEND || intent.type != "text/plain") return null
        val url = Regex("https://[^\\s]+").findAll(intent.getStringExtra(Intent.EXTRA_TEXT).orEmpty())
            .map { it.value }.firstOrNull { YouTubeNavigation.isYouTubeUrl(it) }
        if (url == null) Toast.makeText(this, R.string.invalid_link, Toast.LENGTH_LONG).show()
        return url
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        val playback = service ?: return
        sharedVideo(intent)?.let { playback.webView.loadUrl(it) }
        intent.action = Intent.ACTION_MAIN
    }

    override fun onExternalLink(uri: Uri) {
        try {
            startActivity(Intent(Intent.ACTION_VIEW, uri).addCategory(Intent.CATEGORY_BROWSABLE))
        } catch (_: ActivityNotFoundException) {
            Toast.makeText(this, R.string.no_browser, Toast.LENGTH_LONG).show()
        }
    }

    override fun onStatus(text: String) {
        status.text = text
    }

    override fun onTitle(title: String) {
        pageTitle.text = title.ifBlank { getString(R.string.app_name) }
    }

    override fun onLocation(url: String) {
        if (url.isNotBlank()) address.setText(url)
        updateNavigationButtons()
    }

    override fun onProgress(progress: Int) {
        findViewById<ProgressBar>(R.id.progress).apply {
            this.progress = progress
            visibility = if (progress == 100) View.GONE else View.VISIBLE
        }
    }

    override fun onStopped() = finish()

    private fun navigate() {
        val destination = YouTubeNavigation.destination(address.text.toString())
        if (destination == null) {
            address.error = getString(R.string.invalid_link)
            return
        }
        address.error = null
        service?.webView?.loadUrl(destination)
        address.clearFocus()
        (getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager)
            .hideSoftInputFromWindow(address.windowToken, 0)
    }

    private fun selectSpeed(rate: Int) {
        service?.selectSpeed(rate)
        updateSpeedButtons()
    }

    private fun updateSpeedButtons() {
        findViewById<Button>(R.id.normal_speed).apply {
            isEnabled = service != null
            isSelected = service?.requestedRate == 1
        }
        findViewById<Button>(R.id.triple_speed).apply {
            isEnabled = service != null
            isSelected = service?.requestedRate == 3
        }
        findViewById<View>(R.id.go).isEnabled = service != null
        findViewById<View>(R.id.home).isEnabled = service != null
        findViewById<View>(R.id.reload).isEnabled = service != null
        updateNavigationButtons()
        updateAdBlockButton()
    }

    private fun updateNavigationButtons() {
        val webView = service?.webView
        findViewById<View>(R.id.back).isEnabled = webView?.canGoBack() == true
        findViewById<View>(R.id.forward).isEnabled = webView?.canGoForward() == true
    }

    private fun updateAdBlockButton() {
        val enabled = service?.adBlockingEnabled
        findViewById<Button>(R.id.ad_block).apply {
            isEnabled = enabled != null
            isSelected = enabled == true
            text = getString(if (enabled == true) R.string.ad_block_on else R.string.ad_block_off)
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

    override fun onPause() {
        CookieManager.getInstance().flush()
        super.onPause()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        val browserState = Bundle()
        if (service?.webView?.saveState(browserState) != null) {
            val parcel = Parcel.obtain()
            try {
                parcel.writeBundle(browserState)
                if (parcel.dataSize() <= MAX_BROWSER_STATE_BYTES) {
                    outState.putBundle(BROWSER_STATE, browserState)
                }
            } finally {
                parcel.recycle()
            }
        }
        super.onSaveInstanceState(outState)
    }

    override fun onDestroy() {
        exitFullscreen()
        service?.let { playback ->
            if (playback.listener === this) {
                playback.listener = null
                playback.resetChromeClient()
                (playback.webView.parent as? ViewGroup)?.removeView(playback.webView)
                playback.webContext.baseContext = applicationContext
            }
        }
        service = null
        if (bound) unbindService(connection)
        bound = false
        super.onDestroy()
    }

    companion object {
        private const val BROWSER_STATE = "browser_state"
        private const val MAX_BROWSER_STATE_BYTES = 512 * 1024
    }
}
