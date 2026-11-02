const form = fragmentElement.querySelector('form');

if (form) {
	form.addEventListener('submit', (event) => {
		event.preventDefault();

		const status = form.querySelector('.kaffora-newsletter__status');

		if (status) {
			status.textContent = 'Thanks! Check your inbox to confirm.';
		}
	});
}
