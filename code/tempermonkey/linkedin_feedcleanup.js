// ==UserScript==
// @name         Hide LinkedIn Suggested Posts
// @namespace    https://github.com/madsamuel
// @version      1.0
// @description  Hides feed items on LinkedIn that are labeled as "Suggested"
// @match        https://www.linkedin.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    /**
     * Hides any LinkedIn posts that contain the word "Suggested"
     */
    function hideSuggestedPosts() {
        // Select all feed items. LinkedIn changes classes frequently;
        // this is a common container for feed updates, but you may need to update it.
        const posts = document.querySelectorAll('div.feed-shared-update-v2, article');

        posts.forEach(post => {
            // Check the text of the post
            if (post.innerText.includes('Suggested')) {
                // Option 1: Completely remove the post
                post.remove();

                // Option 2 (alternative): just hide the post visually
                // post.style.display = 'none';
            }
        });
    }

    // Use a MutationObserver to handle dynamically loaded feed items
    const observer = new MutationObserver(() => {
        hideSuggestedPosts();
    });

    // Observe the entire document for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Initial run
    hideSuggestedPosts();
})();