// ==UserScript==
// @name         Hide LinkedIn Suggested Posts
// @namespace    https://github.com/madsamuel
// @version      1.1
// @description  Hides feed items on LinkedIn that are labeled as "Suggested"
// @match        https://www.linkedin.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    /**
     * Configuration
     */
    const FEED_ITEM_SELECTORS = [
        'div.feed-shared-update-v2', // Common container
        'article'                    // Fallback selector for feed items
    ];
    const KEYWORD = 'Suggested';      // Hide posts containing this text
    const DEBUG_LOG = false;          // Set to true to see console.debug statements

    /**
     * Logs messages to console if DEBUG_LOG is enabled.
     */
    function debugLog(...args) {
        if (DEBUG_LOG) {
            console.debug('[HideLinkedInSuggested]', ...args);
        }
    }

    /**
     * Hide any LinkedIn posts that contain the KEYWORD in a specific area.
     * If LinkedIn changes markup, adjust selectors or text checks accordingly.
     */
    function hideSuggestedPosts() {
        const selector = FEED_ITEM_SELECTORS.join(',');
        const posts = document.querySelectorAll(selector);

        posts.forEach(post => {
            // Option A: Check entire post text:
            // if (post.innerText.includes(KEYWORD)) { ... }

            // Option B (preferred): Look for a child element that specifically
            // contains the "Suggested" text. This reduces false positives.
            // LinkedIn often marks "Suggested" near the post heading or subheading.
            const possibleLabel = post.querySelector('span, h2, h3, .feed-shared-header__text');
            if (possibleLabel && possibleLabel.innerText.includes(KEYWORD)) {
                debugLog('Removing post with suggested label:', post);

                // Remove the post from the DOM
                post.remove();
            }
        });
    }

    /**
     * Observer callback to handle dynamically loaded feed items.
     * Minimizes repeated scans by throttling or short-circuiting if needed.
     */
    function onMutations(mutationList) {
        // We could optimize further, e.g., only call hideSuggestedPosts()
        // if we detect changes in specific feed containers. For simplicity,
        // we just re-check each time there's a mutation.
        hideSuggestedPosts();
    }

    /**
     * Set up a MutationObserver to watch for feed changes.
     * This captures new posts loaded as you scroll or refresh partial page content.
     */
    const observer = new MutationObserver(onMutations);

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Initial run
    hideSuggestedPosts();
})();
