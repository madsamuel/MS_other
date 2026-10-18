package com.madsamuel.youtube3x

import java.net.URI
import java.net.URISyntaxException
import java.util.Locale

object AdBlockRules {
    private val adDomains = setOf(
        "doubleclick.net",
        "googlesyndication.com",
        "googleadservices.com"
    )
    private val youtubeAdPaths = listOf("/pagead/", "/api/stats/ads", "/ptracking")

    fun shouldBlock(url: String, enabled: Boolean = true): Boolean {
        if (!enabled) return false
        val uri = try {
            URI(url)
        } catch (_: URISyntaxException) {
            return false
        }
        if (uri.scheme?.lowercase(Locale.ROOT) !in setOf("http", "https")) return false
        val host = uri.host?.lowercase(Locale.ROOT) ?: return false
        if (adDomains.any { host == it || host.endsWith(".$it") }) return true
        if (host != "youtube.com" && !host.endsWith(".youtube.com")) return false
        val path = uri.path ?: return false
        return youtubeAdPaths.any {
            if (it.endsWith("/")) path.startsWith(it) else path == it || path.startsWith("$it/")
        }
    }
}
