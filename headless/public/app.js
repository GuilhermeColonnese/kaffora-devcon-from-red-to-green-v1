// CSR: a typical single-page app. The server sends an empty shell; this script
// fetches the data and renders the page in the browser.
import {CSS, META, jsonLd, renderApp} from '/render.mjs';

const style = document.createElement('style');

style.textContent = CSS;
document.head.append(style);

document.title = META.title;

const description = document.createElement('meta');

description.name = 'description';
description.content = META.description;
document.head.append(description);

const response = await fetch('/api/coffees');
const {coffees, source} = await response.json();

document.getElementById('app').innerHTML = renderApp(coffees, source);

const ld = document.createElement('script');

ld.type = 'application/ld+json';
ld.textContent = JSON.stringify(jsonLd(coffees, location.origin));
document.head.append(ld);
