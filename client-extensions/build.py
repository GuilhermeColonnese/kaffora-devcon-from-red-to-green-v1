"""Build dist/kaffora-cx.zip, a Liferay client extension archive, without Gradle.

Same layout Liferay Workspace produces: <project>.client-extension-config.json at the
root and the frontend files under static/ (served at /o/kaffora-cx/...). Also copies the
archive to docker/profiles/{red,green}/osgi/client-extensions/, so Liferay installs it on every
(re)start of the container, in both profiles.

    python3 client-extensions/build.py
"""
import json
import os
import shutil
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "kaffora-cx"
SRC = os.path.join(HERE, PROJECT, "static")
DIST = os.path.join(HERE, "dist")
PROFILES = [os.path.join(HERE, "..", "docker", "profiles", p, "osgi", "client-extensions") for p in ("red", "green")]
CET = "com.liferay.client.extension.type.configuration.CETConfiguration~"


def entry(key, name, type_, type_settings):
    return CET + key, {
        ":configurator:policy": "force",
        "baseURL": "${portalURL}/o/" + PROJECT,
        "description": "",
        "dxp.lxc.liferay.com.virtualInstanceId": "default",
        "name": name,
        "projectId": PROJECT,
        "projectName": PROJECT,
        "properties": [],
        "sourceCodeURL": "",
        "type": type_,
        "typeSettings": type_settings,
        "webContextPath": "/" + PROJECT,
    }


config = dict([
    entry("kaffora-brand-fonts", "Kaffora Brand Fonts (self-hosted, optional display)", "globalCSS",
          ["url=kaffora-brand-fonts.css"]),
    entry("kaffora-tags", "Kaffora Tags (governed)", "globalJS",
          ["url=kaffora-tags.js", "scriptLocation=bottom", 'scriptElementAttributesJSON={"async":true}']),
])

os.makedirs(DIST, exist_ok=True)
out = os.path.join(DIST, PROJECT + ".zip")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr(PROJECT + ".client-extension-config.json", json.dumps(config, indent="\t") + "\n")
    z.writestr("WEB-INF/", "")
    z.writestr("WEB-INF/liferay-plugin-package.properties",
               f"Bundle-SymbolicName={PROJECT}\nLiferay-Client-Extension-Frontend=static/\nmodule-group-id=liferay\nname={PROJECT}\n")
    z.writestr("static/", "")
    for root, dirs, files in os.walk(SRC):
        rel = os.path.relpath(root, SRC)
        if rel != ".":
            z.writestr("static/" + rel.replace(os.sep, "/") + "/", "")
        for f in sorted(files):
            arc = "static/" + ("" if rel == "." else rel.replace(os.sep, "/") + "/") + f
            z.write(os.path.join(root, f), arc)

# The Liferay image copies /mnt/liferay/files (the mounted profile) into /opt/liferay on every
# start, so the archive lands in /opt/liferay/osgi/client-extensions in both profiles.
for d in PROFILES:
    os.makedirs(d, exist_ok=True)
    shutil.copy(out, d)
print(f"Built {os.path.relpath(out, os.path.join(HERE, '..'))} and copied it to docker/profiles/{{red,green}}/osgi/client-extensions/")
