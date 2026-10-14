(function (requestedRate) {
    "use strict";
    if (!window.youtube3xController) {
        let desiredRate = requestedRate;
        let error = null;
        const attached = new WeakSet();
        const isAd = () => Boolean(document.querySelector(".ad-showing, .ad-interrupting"));
        function apply(video) {
            if (isAd()) return;
            try {
                video.preservesPitch = true;
                if (video.playbackRate !== desiredRate) video.playbackRate = desiredRate;
                error = null;
            } catch (failure) {
                error = failure.message || String(failure);
            }
        }
        window.youtube3xController = {
            update(rate) {
                desiredRate = rate;
                const videos = Array.from(document.querySelectorAll("video"));
                videos.forEach(video => {
                    if (!attached.has(video)) {
                        attached.add(video);
                        ["loadedmetadata", "play", "ratechange"].forEach(event => {
                            video.addEventListener(event, () => apply(video));
                        });
                    }
                    apply(video);
                });
                const active = videos.find(video => !video.paused && video.readyState > 0) ||
                    videos.find(video => video.readyState > 0);
                return JSON.stringify({
                    found: Boolean(active) && !isAd(),
                    actual: active ? active.playbackRate : null,
                    adError: window.youtube3xAdBlocker ? window.youtube3xAdBlocker.error : null,
                    error: error
                });
            }
        };
    }
    return window.youtube3xController.update(requestedRate);
})(__REQUESTED_RATE__);
