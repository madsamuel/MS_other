const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const assets = path.resolve(__dirname, "../../main/assets");
const background = fs.readFileSync(path.join(assets, "background-playback.js"), "utf8");
const speed = fs.readFileSync(path.join(assets, "playback-speed.js"), "utf8");

test("exposes a visible document and intercepts visibility changes only once", () => {
    const listeners = [];
    const document = { hidden: true, visibilityState: "hidden" };
    const context = vm.createContext({
        document,
        window: { addEventListener: (...args) => listeners.push(args) }
    });
    vm.runInContext(background, context);
    vm.runInContext(background, context);
    assert.equal(document.hidden, false);
    assert.equal(document.visibilityState, "visible");
    assert.equal(document.webkitHidden, false);
    assert.equal(document.webkitVisibilityState, "visible");
    assert.equal(listeners.length, 2);
    let stopped = false;
    listeners[0][1]({ stopImmediatePropagation: () => { stopped = true; } });
    assert.equal(stopped, true);
    assert.equal(listeners[0][2], true);
});

test("tracks media playback without overriding user pause or end", () => {
    const video = {
        paused: true, ended: false, readyState: 4, playbackRate: 1, duration: 0, currentTime: 0,
        addEventListener() {}
    };
    const context = vm.createContext({
        window: {},
        document: { title: "Test video", querySelectorAll: () => [video], querySelector: () => null }
    });
    const run = () => JSON.parse(vm.runInContext(speed.replace("__REQUESTED_RATE__", "3"), context));
    assert.equal(run().playing, false);
    assert.equal(video.paused, true);
    video.paused = false;
    assert.equal(run().playing, true);
    assert.equal(run().actual, 3);
    assert.equal(run().position, 0);
    assert.equal(run().duration, 0);
    assert.equal(run().title, "Test video");
    video.ended = true;
    assert.equal(run().playing, false);
    video.paused = true;
    context.window.youtube3xPlayError = "Playback rejected";
    assert.equal(run().commandError, "Playback rejected");
});
