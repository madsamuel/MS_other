package com.madsamuel.youtube3x

import java.net.URI
import java.net.URISyntaxException
import java.net.URLEncoder

object YouTubeNavigation {
    const val HOME = "https://m.youtube.com/"
    private val hosts = setOf("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be")

    fun isYouTubeUrl(value: String): Boolean {
        val uri = try {
            URI(value)
        } catch (_: URISyntaxException) {
            return false
        }
        return uri.scheme.equals("https", ignoreCase = true) &&
            uri.host?.lowercase() in hosts && uri.rawUserInfo == null &&
            (uri.port == -1 || uri.port == 443)
    }

    fun destination(input: String): String? {
        val value = input.trim()
        if (value.isEmpty()) return null
        val candidate = if (hosts.any { value.startsWith("$it/", ignoreCase = true) } ||
            value.lowercase() in hosts
        ) "https://$value" else value
        if (isYouTubeUrl(candidate)) return candidate
        if (value.contains("://") || value.startsWith("http:", ignoreCase = true) ||
            value.startsWith("https:", ignoreCase = true)
        ) return null
        return "${HOME}results?search_query=${URLEncoder.encode(value, "UTF-8")}"
    }
}
