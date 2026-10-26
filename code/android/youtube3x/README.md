# YouTube 3x

A standalone Kotlin Android app (Android 8.0+) that browses the mobile YouTube
website in a WebView and requests 3x playback using the HTML video playback rate.
No API key, video downloading, or stream extraction is needed.

## Run

Open this directory in Android Studio, let Gradle sync, and run `app` on a device
or emulator. Use Android Studio's bundled JDK (17 or newer) and Android SDK 36.
Android Studio creates the untracked `local.properties` SDK path.

From PowerShell, with `JAVA_HOME` and the SDK configured:

```powershell
.\gradlew.bat :app:assembleDebug :app:testDebugUnitTest
node --test app\src\test\js\*.test.cjs
```

The installable debug APK is `app\build\outputs\apk\debug\app-debug.apk`.

## Use

Browse YouTube, search from the app's search field, or paste a YouTube URL.
You can also share a YouTube link from another app to **YouTube 3x**.
Start the video yourself; the app defaults to 3x. Use **1x** or **3x** to switch
speeds. The choice is remembered, and reapplied as YouTube changes videos or
resets the playback rate. The status shows the actual rate, not just the request.
YouTube's fullscreen control is supported; Back exits fullscreen or goes back.
The top bar also provides Back and Forward navigation, and the current page title
is shown above the player. The media notification and lock screen show the video
title and playback position. The playback notification and foreground service
are active only while media is playing.
Playback continues when you switch apps, press Home or Back at the root page,
or lock the screen. The player is owned by a media foreground service rather
than the activity. While media is playing, the notification and lock screen show
the video title and playback position, with **Pause** and **Stop** controls.
Pausing removes the ongoing notification; reopen the app to resume. **Stop** ends
the session and closes the app. Removing the app from Recents also stops
playback. Another app taking audio focus pauses playback; resume manually
afterwards. Media playback controls do not require notification permission. The
service and partial wake lock are active only while media is playing.

The toolbar uses labeled navigation icons and highlights the selected playback
speed. The search field accepts search terms or YouTube links.

Ad blocking is enabled by default and can be toggled with **Ad block on/off**. When
enabled, known advertising domains and YouTube ad
endpoints are blocked, recognized display-ad elements are hidden, and detected
player ads are skipped using a visible Skip button or seeking to the end of a
finite ad. Normal video streams are not blocked. If seeking fails, the app
reports it in the status line.

## Limitations

This is an unofficial browser-based player, not the official YouTube app.
3x relies on YouTube exposing an HTML video element in Android WebView; live
streams, restricted videos, and future website changes may prevent it.
Ad blocking is best-effort, not a guarantee: server-inserted ads sharing a video
stream, unrecognized ad formats, and YouTube anti-adblock measures may still
show ads or prevent playback. Internet access and an up-to-date Android System
WebView are required. Google sign-in inside embedded browsers may be blocked;
signed-out browsing is the intended starting experience. Non-YouTube HTTPS links
that you tap open externally. Downloads are not provided.

Background playback depends on Android System WebView and YouTube's player.
Keep WebView updated: document-start script support improves protection against
YouTube pausing on visibility changes. Manufacturer battery restrictions,
force-stopping the app, or Android reclaiming its process can stop playback;
the app does not restart playback automatically after being killed. Keeping the
web player alive uses more battery than a dedicated audio-only player.

## Device smoke checks

Before release, repeat these checks on each supported Android major version with
the latest Android System WebView:

1. Open a standard YouTube video, verify audio/video playback and both 1x and 3x
   rates; navigate to another video and confirm the selected rate is reapplied.
2. Verify fullscreen entry/exit, Back/Forward history, shared video links, and
   that tapping a non-YouTube HTTPS link opens the external browser.
3. While playing, switch apps and lock the screen; confirm playback continues,
   the notification/lock screen show the video title and position, and Pause
   and Stop work. Pause playback and confirm the ongoing notification is removed;
   reopen the app to resume.
4. Toggle ad blocking off and on, navigate/reload, and confirm the choice
   persists. Check that a normal video still plays in both modes.
5. Repeat with a live stream and a restricted video, and after a network
   interruption. Confirm the status is
   understandable and Reload recovers from a failed page load.
