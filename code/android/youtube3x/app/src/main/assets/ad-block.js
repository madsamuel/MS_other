(function () {
    "use strict";
    if (window.youtube3xAdBlocker) {
        window.youtube3xAdBlocker.update();
        return;
    }
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
    window.youtube3xAdBlocker = {
        update,
        get error() { return error; }
    };
    const observer = new MutationObserver(update);
    observer.observe(document, { childList: true, subtree: true, attributes: true,
        attributeFilter: ["class", "disabled"] });
    update();
})();
