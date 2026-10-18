(function () {
    "use strict";
    if (window.youtube3xBackgroundPlayback) return;
    // YouTube pauses on document visibility changes even if WebView stays resumed.
    Object.defineProperties(document, {
        hidden: { configurable: true, get: () => false },
        visibilityState: { configurable: true, get: () => "visible" },
        webkitHidden: { configurable: true, get: () => false },
        webkitVisibilityState: { configurable: true, get: () => "visible" }
    });
    const ignoreVisibilityChange = event => event.stopImmediatePropagation();
    window.addEventListener("visibilitychange", ignoreVisibilityChange, true);
    window.addEventListener("webkitvisibilitychange", ignoreVisibilityChange, true);
    window.youtube3xBackgroundPlayback = true;
})();
