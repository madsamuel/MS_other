const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const assets = path.resolve(__dirname, "../../main/assets");
const adScript = fs.readFileSync(path.join(assets, "ad-block.js"), "utf8");
const speedScript = fs.readFileSync(path.join(assets, "playback-speed.js"), "utf8");

function page({ ad = false, skip = false, duration = 30, seekFails = false } = {}) {
    let clicks = 0;
    let observerCallback;
    let observing = false;
    const styles = [];
    let currentTime = 0;
    const video = {
        duration, playbackRate: 1, readyState: 4, paused: false,
        get currentTime() { return currentTime; },
        set currentTime(value) {
            if (seekFails) throw new Error("Seeking restricted");
            currentTime = value;
        },
        addEventListener() {}
    };
    const button = {
        disabled: false,
        getClientRects: () => skip ? [{}] : [],
        click: () => { clicks++; }
    };
    const player = {
        querySelectorAll: () => [button],
        querySelector: () => video
    };
    const document = {
        documentElement: { appendChild: style => styles.push(style) },
        getElementById: id => styles.find(style => style.id === id),
        createElement: () => ({
            remove() {
                const index = styles.indexOf(this);
                if (index >= 0) styles.splice(index, 1);
            }
        }),
        querySelectorAll: selector => selector === "video" ? [video] : ad ? [player] : [],
        querySelector: () => ad ? player : null
    };
    const context = vm.createContext({
        window: {}, document,
        MutationObserver: class {
            constructor(callback) { observerCallback = callback; }
            observe() { observing = true; }
            disconnect() { observing = false; }
        }
    });
    return {
        video, styles, context,
        clicks: () => clicks,
        setAd: value => { ad = value; if (observing) observerCallback(); },
        setEnabled: value => context.window.youtube3xAdBlocker.setEnabled(value),
        run: (enabled = true) =>
            vm.runInContext(adScript.replace("__AD_BLOCK_ENABLED__", String(enabled)), context),
        speed: () => JSON.parse(vm.runInContext(speedScript.replace("__REQUESTED_RATE__", "3"), context))
    };
}

test("does not seek normal content; retains 3x playback", () => {
    const fixture = page();
    fixture.run();
    assert.equal(fixture.video.currentTime, 0);
    assert.equal(fixture.clicks(), 0);
    assert.equal(fixture.speed().actual, 3);
    fixture.run();
    assert.equal(fixture.styles.length, 1);
});

test("prefers the visible Skip button over seeking", () => {
    const fixture = page({ ad: true, skip: true });
    fixture.run();
    assert.equal(fixture.clicks(), 1);
    assert.equal(fixture.video.currentTime, 0);
});

test("seeks finite ads and reapplies 3x when content resumes", () => {
    const fixture = page({ ad: true });
    fixture.run();
    assert.equal(fixture.video.currentTime, 30);
    assert.equal(fixture.speed().found, false);
    fixture.setAd(false);
    assert.equal(fixture.speed().actual, 3);
});

test("does not seek ads with unknown or infinite duration", () => {
    for (const duration of [NaN, Infinity, 0]) {
        const fixture = page({ ad: true, duration });
        fixture.run();
        assert.equal(fixture.video.currentTime, 0);
    }
});

test("surfaces ad-seeking failures without breaking speed status", () => {
    const fixture = page({ ad: true, seekFails: true });
    fixture.run();
    assert.equal(fixture.speed().adError, "Seeking restricted");
    fixture.setAd(false);
    assert.equal(fixture.speed().adError, null);
});

test("handles ads introduced after initial page load", () => {
    const fixture = page();
    fixture.run();
    fixture.setAd(true);
    assert.equal(fixture.video.currentTime, 30);
});

test("can disable and re-enable cosmetic and player ad handling", () => {
    const fixture = page({ ad: true });
    fixture.run(false);
    assert.equal(fixture.video.currentTime, 0);
    assert.equal(fixture.styles.length, 0);
    fixture.setEnabled(true);
    assert.equal(fixture.video.currentTime, 30);
    assert.equal(fixture.styles.length, 1);
    fixture.setEnabled(false);
    assert.equal(fixture.styles.length, 0);
});
