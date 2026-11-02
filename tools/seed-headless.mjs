// Seed Liferay with the "Coffee" object and three entries, so the headless front reads real
// Liferay content (GET /o/c/coffees). Idempotent: safe to run twice.
//
//   node tools/seed-headless.mjs                       (asks Liferay at http://localhost:8080)
//   LIFERAY_URL=http://localhost:8080 LIFERAY_AUTH="test@liferay.com:test" node tools/seed-headless.mjs
//
// PowerShell:  $env:LIFERAY_AUTH="test@liferay.com:test"; node tools/seed-headless.mjs
//
// If anything fails, the headless front still works with headless/data/coffees.json.
import {readFile} from 'node:fs/promises';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const BASE = (process.env.LIFERAY_URL || 'http://localhost:8080').replace(/\/$/, '');
const AUTH = process.env.LIFERAY_AUTH || 'test@liferay.com:test';
const ERC = 'KAFFORA_COFFEE';

const headers = {
	Accept: 'application/json',
	Authorization: `Basic ${Buffer.from(AUTH).toString('base64')}`,
	'Content-Type': 'application/json',
};

async function call(method, path, body) {
	const response = await fetch(`${BASE}${path}`, {body: body ? JSON.stringify(body) : undefined, headers, method});
	const text = await response.text();

	if (!response.ok) {
		throw new Error(`${method} ${path} → HTTP ${response.status}: ${text.slice(0, 300)}`);
	}

	return text ? JSON.parse(text) : {};
}

const field = (name, label, businessType, DBType, required = false) => ({
	DBType,
	businessType,
	indexed: true,
	indexedAsKeyword: false,
	label: {en_US: label},
	name,
	required,
	type: DBType,
});

async function main() {
	console.log(`Liferay: ${BASE}`);

	const {items = []} = await call('GET', '/o/object-admin/v1.0/object-definitions?pageSize=200');
	let definition = items.find((d) => d.externalReferenceCode === ERC || d.name === 'Coffee');

	if (!definition) {
		console.log('Creating object definition "Coffee"…');
		definition = await call('POST', '/o/object-admin/v1.0/object-definitions', {
			externalReferenceCode: ERC,
			label: {en_US: 'Coffee'},
			name: 'Coffee',
			objectFields: [
				field('name', 'Name', 'Text', 'String', true),
				field('origin', 'Origin', 'Text', 'String'),
				field('notes', 'Tasting notes', 'LongText', 'Clob'),
				field('price', 'Price (EUR)', 'Integer', 'Integer'),
				field('weight', 'Weight', 'Text', 'String'),
				field('image', 'Image key', 'Text', 'String'),
			],
			panelCategoryKey: 'control_panel.object',
			pluralLabel: {en_US: 'Coffees'},
			scope: 'company',
		});
	}
	else {
		console.log(`Object definition "Coffee" already exists (id ${definition.id}).`);
	}

	if (definition.status?.code !== 0) {
		console.log('Publishing…');
		definition = await call('POST', `/o/object-admin/v1.0/object-definitions/${definition.id}/publish`);
	}

	const coffees = JSON.parse(await readFile(join(HERE, '..', 'headless', 'data', 'coffees.json'), 'utf8'));

	for (const coffee of coffees) {
		await call('PUT', `/o/c/coffees/by-external-reference-code/${coffee.externalReferenceCode}`, coffee);
		console.log(`  ✓ ${coffee.name}`);
	}

	const check = await call('GET', '/o/c/coffees?pageSize=20');

	console.log(`\nDone: ${check.totalCount ?? check.items?.length} coffees at ${BASE}/o/c/coffees`);
	console.log('Start the front with the same LIFERAY_AUTH: node headless/server.mjs');
}

main().catch((error) => {
	console.error(`\nSeed failed: ${error.message}`);
	console.error('The headless front will use headless/data/coffees.json instead. Create the object by hand if you want:');
	console.error('Control Panel → Objects → + → Coffee (fields: name, origin, notes, price, weight, image), Publish, then add the 3 entries.');
	process.exit(1);
});
