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
```

The installable debug APK is `app\build\outputs\apk\debug\app-debug.apk`.

## Use

Browse YouTube, search from the app's search field, or paste a YouTube URL.
You can also share a YouTube link from another app to **YouTube 3x**.
Start the video yourself; the app defaults to 3x. Use **1x** or **3x** to switch
speeds. The choice is remembered, and reapplied as YouTube changes videos or
resets the playback rate. The status shows the actual rate, not just the request.
YouTube's fullscreen control is supported; Back exits fullscreen or goes back.
Playback pauses when the app leaves the foreground.

## Limitations

This is an unofficial browser-based player, not the official YouTube app.
3x relies on YouTube exposing an HTML video element in Android WebView; live
streams, restricted videos, and future website changes may prevent it. Ads are
not skipped or speed-adjusted. Internet access and an up-to-date Android System
WebView are required. Google sign-in inside embedded browsers may be blocked;
signed-out browsing is the intended starting experience. Non-YouTube HTTPS links
that you tap open externally. No background playback or downloads are provided.
