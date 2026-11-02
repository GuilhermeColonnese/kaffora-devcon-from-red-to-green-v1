// Open a file with the operating system's default app (macOS, Windows, Linux).
import {spawn} from 'node:child_process';

export function openFile(path) {
	const [command, args] =
		process.platform === 'darwin' ? ['open', [path]]
			: process.platform === 'win32' ? ['cmd', ['/c', 'start', '""', path]]
				: ['xdg-open', [path]];

	try {
		spawn(command, args, {detached: true, stdio: 'ignore'}).unref();
	}
	catch {
		console.log(`Open ${path} in your browser.`);
	}
}
