/*
 * "Tag soup": snippets pasted into the site JavaScript field by different teams over the years.
 * Every line below is a real-world anti-pattern that Lighthouse 13 flags.
 */

// 1) Legacy "analytics" fingerprinting the visitor with synchronous work on the main thread.
window.addEventListener('load', function () {
	setTimeout(function () {
		var start = Date.now();
		var fingerprint = 0;

		while (Date.now() - start < 600) {
			fingerprint += Math.sqrt(Math.random() * 1e6);
		}

		window.__kafforaFingerprint = fingerprint;
	}, 50);
});

// 2) Vendor libraries nobody uses anymore (unused + legacy JavaScript, third parties).
['https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.4/jquery.min.js',
	'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.30.1/moment-with-locales.min.js',
	'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js'].forEach(function (src) {
	var script = document.createElement('script');

	script.src = src;
	document.head.appendChild(script);
});

// 3) Promo bar injected at the top of the page after load (layout shift).
setTimeout(function () {
	var bar = document.createElement('div');

	bar.setAttribute('style', 'background:#ffe08a;color:#3b2f00;font-weight:600;padding:18px 16px;text-align:center;');
	bar.textContent = 'Flash sale: 40% off your first subscription. Ends Sunday!';

	var target = document.getElementById('main-content') || document.body;

	target.insertBefore(bar, target.firstChild);
}, 1500);

// 4) Permission prompts on page load.
if (navigator.geolocation) {
	navigator.geolocation.getCurrentPosition(function () {}, function () {});
}

if ('Notification' in window && Notification.permission === 'default') {
	Notification.requestPermission();
}

// 5) "Security" team asked to block pasting into e-mail fields.
document.addEventListener('DOMContentLoaded', function () {
	document.querySelectorAll('input[type="email"]').forEach(function (input) {
		input.addEventListener('paste', function (event) {
			event.preventDefault();
		});
	});
});

// 6) Tracker that was removed from the page years ago (console error).
setTimeout(function () {
	window.legacyTracker.track('pageview');
}, 0);
