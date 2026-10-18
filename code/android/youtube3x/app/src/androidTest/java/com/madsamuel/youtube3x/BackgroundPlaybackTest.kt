package com.madsamuel.youtube3x

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.IBinder
import android.util.Base64
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

@RunWith(AndroidJUnit4::class)
class BackgroundPlaybackTest {
    private val instrumentation = InstrumentationRegistry.getInstrumentation()

    @Test fun continuesWhenHiddenAndDetachedAndRespondsToMediaControls() {
        val context = instrumentation.targetContext
        val connected = CountDownLatch(1)
        lateinit var playback: PlaybackService
        val connection = object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName, binder: IBinder) {
                playback = (binder as PlaybackService.LocalBinder).service
                connected.countDown()
            }
            override fun onServiceDisconnected(name: ComponentName) {}
        }
        val scenario = ActivityScenario.launch(MainActivity::class.java)
        val bound = context.bindService(Intent(context, PlaybackService::class.java), connection, Context.BIND_AUTO_CREATE)
        try {
            assertTrue(connected.await(10, TimeUnit.SECONDS))
            val html = "<video id='video' autoplay src='data:audio/wav;base64,${wave()}'></video>" +
                "<script>document.addEventListener('visibilitychange',()=>video.pause());</script>"
            instrumentation.runOnMainSync {
                playback.webView.stopLoading()
                playback.webView.settings.mediaPlaybackRequiresUserGesture = false
                playback.selectSpeed(3)
                playback.webView.loadDataWithBaseURL(YouTubeNavigation.HOME, html, "text/html", "UTF-8", null)
            }
            await(diagnostics = {
                evaluate(playback, """
                    JSON.stringify({
                        url: location.href,
                        video: Boolean(document.querySelector('video')),
                        paused: document.querySelector('video')?.paused,
                        time: document.querySelector('video')?.currentTime,
                        ready: document.querySelector('video')?.readyState,
                        rate: document.querySelector('video')?.playbackRate,
                        error: document.querySelector('video')?.error?.message
                    })
                """.trimIndent()) + " Status: " + playback.statusText
            }) {
                evaluate(playback, "Boolean(document.querySelector('video') && !video.paused && video.playbackRate === 3)") == "true"
            }
            scenario.onActivity { it.moveTaskToBack(true) }
            assertAdvancing(playback)
            shell("input keyevent 223")
            assertAdvancing(playback)
            shell("input keyevent 224")
            shell("wm dismiss-keyguard")
            // The service owns playback even after the activity is destroyed.
            scenario.close()
            assertAdvancing(playback)
            val reopened = ActivityScenario.launch(MainActivity::class.java)
            try {
                assertAdvancing(playback)
                context.startService(Intent(context, PlaybackService::class.java).setAction("pause"))
                await { evaluate(playback, "video.paused") == "true" }
                val pausedAt = evaluate(playback, "video.currentTime").toDouble()
                Thread.sleep(700)
                assertEquals(pausedAt, evaluate(playback, "video.currentTime").toDouble(), 0.1)
                context.startService(Intent(context, PlaybackService::class.java).setAction("play"))
                await { evaluate(playback, "!video.paused") == "true" }
                assertAdvancing(playback)
                context.startService(Intent(context, PlaybackService::class.java).setAction("stop"))
                await { evaluate(playback, "video.paused") == "true" }
            } finally {
                reopened.close()
            }
        } finally {
            shell("input keyevent 224")
            scenario.close()
            if (bound) context.unbindService(connection)
            context.stopService(Intent(context, PlaybackService::class.java))
        }
    }

    private fun assertAdvancing(service: PlaybackService) {
        val before = evaluate(service, "video.currentTime").toDouble()
        Thread.sleep(1200)
        assertEquals("true", evaluate(service, "!video.paused"))
        assertTrue("Playback stopped progressing in background",
            evaluate(service, "video.currentTime").toDouble() > before + 1)
        assertEquals("3", evaluate(service, "video.playbackRate"))
        assertEquals("\"visible\"", evaluate(service, "document.visibilityState"))
    }

    private fun evaluate(service: PlaybackService, script: String): String {
        val done = CountDownLatch(1)
        var result = ""
        instrumentation.runOnMainSync {
            service.webView.evaluateJavascript(script) {
                result = it
                done.countDown()
            }
        }
        assertTrue("JavaScript did not respond", done.await(5, TimeUnit.SECONDS))
        return result
    }

    private fun await(diagnostics: () -> String = { "" }, condition: () -> Boolean) {
        val deadline = System.currentTimeMillis() + 30000
        while (!condition()) {
            assertTrue("Timed out waiting for playback: ${diagnostics()}", System.currentTimeMillis() < deadline)
            Thread.sleep(150)
        }
    }

    private fun shell(command: String) {
        instrumentation.uiAutomation.executeShellCommand(command).use {
            java.io.FileInputStream(it.fileDescriptor).use { stream -> stream.readBytes() }
        }
    }

    private fun wave(): String {
        val size = 8000 * 60 * 2
        val bytes = ByteBuffer.allocate(44 + size).order(ByteOrder.LITTLE_ENDIAN)
        bytes.put("RIFF".toByteArray()).putInt(36 + size).put("WAVEfmt ".toByteArray())
            .putInt(16).putShort(1).putShort(1).putInt(8000).putInt(16000)
            .putShort(2).putShort(16).put("data".toByteArray()).putInt(size)
        // Silence still exercises the real WebView media pipeline without network access.
        return Base64.encodeToString(bytes.array(), Base64.NO_WRAP)
    }
}
