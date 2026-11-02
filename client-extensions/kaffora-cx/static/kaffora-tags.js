/*
 * Kaffora tags, the governed way (JavaScript client extension, type globalJS).
 *
 * What the free-text JavaScript field did          What this file does instead
 * ------------------------------------------------  ---------------------------------------------
 * 600 ms synchronous loop on load                   nothing on the critical path: async, page
 *                                                   bottom, work deferred to requestIdleCallback
 * jQuery, Moment, Lodash from a CDN, unused         no dependencies (~1 KB)
 * promo bar injected after 1.5 s (layout shift)     no DOM injection: banners are fragments
 * geolocation + notification prompts on load        no permission prompts, ever, on load
 * paste blocked on e-mail fields                    no input hijacking
 * window.legacyTracker.track() → console error      defensive dataLayer, no globals assumed
 *
 * Versioned in Git, reviewed like code, scoped per site (Pages ⚙ → client extensions).
 */
(function () {
	'use strict';

	var dataLayer = (window.dataLayer = window.dataLayer || []);

	function push(event) {
		event.ts = Date.now();
		dataLayer.push(event);
	}

	function start() {
		// Respect privacy signals before measuring anything.
		if (navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true) {
			return;
		}

		push({event: 'page_view', path: location.pathname});

		document.addEventListener(
			'click',
			function (event) {
				var target = event.target && event.target.closest && event.target.closest('a, button');

				if (target) {
					push({
						event: 'cta_click',
						label: (target.getAttribute('aria-label') || target.textContent || '').trim().slice(0, 60),
					});
				}
			},
			{passive: true}
		);
	}

	if ('requestIdleCallback' in window) {
		window.requestIdleCallback(start, {timeout: 3000});
	}
	else {
		window.setTimeout(start, 2000);
	}
})();
