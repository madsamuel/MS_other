package com.madsamuel.youtube3x

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AdBlockRulesTest {
    @Test fun blocksKnownAdvertisingRequests() {
        listOf(
            "https://doubleclick.net/ad",
            "https://googleads.g.doubleclick.net/pagead/ads",
            "https://PAGEAD2.GOOGLESYNDICATION.COM/pagead/js/adsbygoogle.js",
            "https://www.googleadservices.com/pagead/conversion",
            "https://www.youtube.com/pagead/adview",
            "https://m.youtube.com/api/stats/ads?event=1",
            "https://www.youtube.com/ptracking?video_id=abc"
        ).forEach { assertTrue(it, AdBlockRules.shouldBlock(it)) }
    }

    @Test fun preservesVideoNavigationAndNonAdvertisingResources() {
        listOf(
            "https://m.youtube.com/watch?v=abc",
            "https://www.youtube.com/youtubei/v1/player",
            "https://www.youtube.com/youtubei/v1/next",
            "https://rr1.googlevideo.com/videoplayback?itag=22",
            "https://i.ytimg.com/vi/abc/hqdefault.jpg",
            "https://consent.youtube.com/",
            "https://www.youtube.com/api/stats/playback",
            "https://www.youtube.com/api/stats/ads-extra",
            "https://notdoubleclick.net/video",
            "https://doubleclick.net.example.com/video",
            "https://example.com/pagead/ads",
            "file:///pagead/ads",
            "https://["
        ).forEach { assertFalse(it, AdBlockRules.shouldBlock(it)) }
    }

    @Test fun canDisableNetworkRequestBlocking() {
        assertFalse(AdBlockRules.shouldBlock("https://doubleclick.net/ad", enabled = false))
    }
}
