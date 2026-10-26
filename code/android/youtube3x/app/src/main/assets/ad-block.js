(function (initiallyEnabled) {
    "use strict";
    if (window.youtube3xAdBlocker) {
        if (window.youtube3xAdBlocker.enabled !== Boolean(initiallyEnabled)) {
            window.youtube3xAdBlocker.setEnabled(initiallyEnabled);
        } else {
            window.youtube3xAdBlocker.update();
        }
        return;
    }
    let enabled = Boolean(initiallyEnabled);
    let error = null;
    const adSelector = ".ad-showing, .ad-interrupting";
    const skipSelector = ".ytp-ad-skip-button, .ytp-ad-skip-button-modern, .ytp-skip-ad-button";
    const cosmeticSelector = [
        "ytd-ad-slot-renderer", "ytm-ad-slot-renderer",
        "ytd-display-ad-renderer", "ytm-display-ad-renderer",
        "ytd-promoted-sparkles-web-renderer", "ytm-promoted-sparkles-web-renderer",
        "ytd-promoted-video-renderer", "ytm-promoted-video-renderer",
        ".ytp-ad-overlay-container"
    ].join(", ");

    function update() {
        if (!enabled) {
            document.getElementById("youtube3x-ad-style")?.remove();
            error = null;
            return;
        }
        if (!document.getElementById("youtube3x-ad-style") && document.documentElement) {
            const style = document.createElement("style");
            style.id = "youtube3x-ad-style";
            style.textContent = cosmeticSelector + " { display: none !important; }";
            (document.head || document.documentElement).appendChild(style);
        }
        error = null;
        document.querySelectorAll(adSelector).forEach(player => {
            const skip = Array.from(player.querySelectorAll(skipSelector))
                .find(button => !button.disabled && button.getClientRects().length > 0);
            if (skip) {
                skip.click();
                return;
            }
            // Seek only inside a player explicitly marked as showing an ad.
            const video = player.querySelector("video");
            if (video && Number.isFinite(video.duration) && video.duration > 0 &&
                video.currentTime < video.duration) {
                try {
                    video.currentTime = video.duration;
                } catch (failure) {
                    error = failure.message || String(failure);
                }
            }
        });
    }
    const observer = new MutationObserver(() => update());
    window.youtube3xAdBlocker = {
        update,
        setEnabled(value) {
            enabled = Boolean(value);
            if (enabled) {
                observer.observe(document, { childList: true, subtree: true, attributes: true,
                    attributeFilter: ["class", "disabled"] });
            } else {
                observer.disconnect();
            }
            update();
        },
        get enabled() { return enabled; },
        get error() { return error; }
    };
    window.youtube3xAdBlocker.setEnabled(enabled);
})(__AD_BLOCK_ENABLED__);
