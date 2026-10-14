package com.madsamuel.youtube3x

import org.junit.Assert.*
import org.junit.Test

class YouTubeNavigationTest {
    @Test fun acceptsOnlySecureYouTubeOrigins() {
        listOf("https://m.youtube.com/watch?v=abc", "https://www.youtube.com/shorts/abc",
            "https://youtu.be/abc", "https://YOUTUBE.COM:443/").forEach {
            assertTrue(it, YouTubeNavigation.isYouTubeUrl(it))
        }
        listOf("http://youtube.com", "https://youtube.com.evil.com", "https://evil.com/youtube.com",
            "https://user@youtube.com", "https://youtube.com:444", "javascript:alert(1)",
            "https://[", "https://consent.youtube.com").forEach {
            assertFalse(it, YouTubeNavigation.isYouTubeUrl(it))
        }
    }

    @Test fun resolvesLinksAndSearches() {
        assertEquals("https://youtu.be/abc", YouTubeNavigation.destination(" youtu.be/abc "))
        assertEquals("https://m.youtube.com", YouTubeNavigation.destination("m.youtube.com"))
        assertEquals("https://m.youtube.com/results?search_query=kotlin+%26+android",
            YouTubeNavigation.destination("kotlin & android"))
        assertNull(YouTubeNavigation.destination(" "))
        assertNull(YouTubeNavigation.destination("https://example.com"))
        assertNull(YouTubeNavigation.destination("http://youtube.com"))
    }
}
