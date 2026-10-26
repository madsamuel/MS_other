package com.madsamuel.youtube3x

import android.view.View
import android.widget.Button
import android.widget.ImageButton
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class ToolbarTest {
    @Test fun controlsFitNarrowScreensAndReflectPlaybackSettings() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        ActivityScenario.launch(MainActivity::class.java).use { scenario ->
            val deadline = System.currentTimeMillis() + 10000
            var ready = false
            while (!ready && System.currentTimeMillis() < deadline) {
                scenario.onActivity { ready = it.findViewById<View>(R.id.normal_speed).isEnabled }
                if (!ready) Thread.sleep(100)
            }
            assertTrue("Playback service did not connect", ready)
            scenario.onActivity { activity ->
                val root = activity.findViewById<View>(R.id.root)
                val density = activity.resources.displayMetrics.density
                val width = (320 * density).toInt()
                val height = root.height
                val normal = activity.findViewById<Button>(R.id.normal_speed)
                val triple = activity.findViewById<Button>(R.id.triple_speed)
                val adBlock = activity.findViewById<Button>(R.id.ad_block)
                val wasNormal = normal.isSelected
                val wasBlocking = adBlock.isSelected
                try {
                    root.measure(
                        View.MeasureSpec.makeMeasureSpec(width, View.MeasureSpec.EXACTLY),
                        View.MeasureSpec.makeMeasureSpec(height, View.MeasureSpec.EXACTLY)
                    )
                    root.layout(0, 0, width, height)
                    for (id in listOf(R.id.home, R.id.back, R.id.forward, R.id.reload, R.id.go)) {
                        val icon = activity.findViewById<ImageButton>(id)
                        assertFalse("Missing accessible label", icon.contentDescription.isNullOrBlank())
                        assertTrue("Touch target too small", icon.width >= (48 * density).toInt())
                        assertTrue("Touch target too small", icon.height >= (48 * density).toInt())
                    }
                    for (button in listOf(normal, triple, adBlock)) {
                        assertEquals("Button text wraps", 1, button.lineCount)
                        assertTrue("Button extends past toolbar", button.right <= (button.parent as View).width)
                        assertTrue("Button extends past toolbar", button.left >= 0)
                    }
                    normal.performClick()
                    assertTrue(normal.isSelected)
                    assertFalse(triple.isSelected)
                    triple.performClick()
                    assertTrue(triple.isSelected)
                    assertFalse(normal.isSelected)
                    adBlock.performClick()
                    assertEquals(!wasBlocking, adBlock.isSelected)
                    assertEquals(activity.getString(
                        if (adBlock.isSelected) R.string.ad_block_on else R.string.ad_block_off
                    ), adBlock.text.toString())
                } finally {
                    if (wasNormal) normal.performClick() else triple.performClick()
                    if (adBlock.isSelected != wasBlocking) adBlock.performClick()
                    root.requestLayout()
                }
            }
        }
    }
}
