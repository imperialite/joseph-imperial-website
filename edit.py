"""Local academic-record editor. Python 3.11+, standard library only."""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from threading import Lock
import time
from urllib.parse import urlparse
import webbrowser

ROOT = Path(__file__).resolve().parent
REPO = "imperialite/joseph-imperial-website"
FILES = ("content.json", "publications.json")
LOCK = Lock()
SESSION = secrets.token_urlsafe(32)
STATUS = (0, {})


class EditableText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.href = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href", "")
            self.parts.append("[")

    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            self.parts.append(f"]({self.href})")
            self.href = None

    def handle_data(self, data):
        self.parts.append(data)


def editable(value):
    parser = EditableText()
    parser.feed(value)
    return "".join(parser.parts)


def safe_url(value, optional=False):
    if optional and not value:
        return value
    parsed = urlparse(value)
    if parsed.scheme not in ("https", "http") or not parsed.netloc or any(c.isspace() for c in value):
        raise ValueError("Links must be complete https:// or http:// addresses.")
    return value


def rich_html(value):
    result, end, cursor = [], 0, 0
    while match := re.search(r"\[([^\]\n]+)\]\(", value[cursor:]):
        start = cursor + match.start()
        url_start = cursor + match.end()
        stop, depth = url_start, 1
        while stop < len(value) and depth:
            if value[stop] == "(":
                depth += 1
            elif value[stop] == ")":
                depth -= 1
            stop += 1
        if depth:
            break
        label, url = match.group(1), value[url_start:stop - 1]
        safe_url(url)
        result.append(escape(value[end:start]))
        result.append(f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>')
        end = cursor = stop
    result.append(escape(value[end:]))
    return "".join(result)


def map_rich(content, transform):
    for key in ("profile", "about", "news"):
        content[key] = [transform(v) for v in content[key]]
    content["publication_note"] = transform(content["publication_note"])
    for key in ("experience", "education", "awards"):
        for item in content[key]:
            item["paragraphs"] = [transform(v) for v in item["paragraphs"]]
    for item in content["media"]:
        item["html"] = transform(item["html"])
    return content


def revision():
    return sha256(b"\0".join((ROOT / f).read_bytes() for f in FILES)).hexdigest()


def load_records():
    content, papers = [json.loads((ROOT / f).read_text(encoding="utf-8")) for f in FILES]
    return {"content": map_rich(content, editable), "publications": papers, "revision": revision()}


def string(value):
    if not isinstance(value, str) or len(value) > 30000:
        raise ValueError("Each field must be text, with a maximum of 30,000 characters.")


def strings(value):
    if not isinstance(value, list) or len(value) > 1000:
        raise ValueError("Each section must contain a list of up to 1,000 records.")
    for item in value:
        string(item)


def records(value, fields):
    if not isinstance(value, list) or len(value) > 1000:
        raise ValueError("Each section must contain a list of up to 1,000 records.")
    for row in value:
        if not isinstance(row, dict):
            raise ValueError("A record is invalid. Reload the editor and try again.")
        for field in fields:
            string(row[field])


def validate(data):
    c, p = data["content"], data["publications"]
    for key in ("profile", "about", "news"):
        strings(c[key])
    string(c["publication_note"])
    for key in ("experience", "education", "awards"):
        records(c[key], ("title", "institution", "date", "note"))
        for row in c[key]:
            strings(row["paragraphs"])
    records(c["media"], ("outlet", "html"))
    records(c["socials"], ("label", "url"))
    for row in c["socials"]:
        safe_url(row["url"])
    for key in ("name", "email", "description", "scholar_url", "cv_url", "github_url", "anthology_url"):
        string(c["site"][key])
        if key.endswith("_url"):
            safe_url(c["site"][key])
    if not re.fullmatch(r"[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+", c["site"]["email"]):
        raise ValueError("Enter a valid contact email address.")
    if not c["site"]["name"].strip():
        raise ValueError("Your name is required.")
    records(p, ("year", "title", "authors", "venue", "topic", "url", "link_label"))
    for row in p:
        safe_url(row["url"], optional=True)
        if not re.fullmatch(r"\d{4}", row["year"]):
            raise ValueError("Publication years must use four digits, for example 2026.")
        if not row["title"].strip():
            raise ValueError("Each publication needs a title.")
        if "featured" in row and not isinstance(row["featured"], bool):
            raise ValueError("Publication highlight must be on or off.")


def save_records(data):
    validate(data)
    if data.get("revision") != revision():
        raise ValueError("These records changed in another window. Copy your unsaved edits, then reload before saving.")
    c = deepcopy(data["content"])
    # Preserve the original source byte for byte when its editable text is unchanged.
    original = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    originals = {}
    map_rich(deepcopy(original), lambda value: originals.setdefault(editable(value), value))
    map_rich(c, lambda value: originals[value] if value in originals else rich_html(value))
    # Keep duplicated contact links consistent when one representation is edited.
    mapping = {"Google Scholar": "scholar_url", "CV": "cv_url", "Github": "github_url", "ACL Anthology": "anthology_url"}
    old_links = {row["label"]: row["url"] for row in original["socials"]}
    for row in c["socials"]:
        key = mapping.get(row["label"])
        if key:
            if c["site"][key] != original["site"][key]:
                row["url"] = c["site"][key]
            elif row["url"] != old_links.get(row["label"]):
                c["site"][key] = row["url"]
    values = (c, data["publications"])
    if all(value == json.loads((ROOT / f).read_text(encoding="utf-8")) for f, value in zip(FILES, values)):
        return revision()
    with tempfile.TemporaryDirectory(prefix=".editor-build-", dir=ROOT) as folder:
        staging = Path(folder)
        shutil.copy2(ROOT / "build.py", staging / "build.py")
        shutil.copytree(ROOT / "dist", staging / "dist")
        for f, value in zip(FILES, values):
            (staging / f).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(staging / "build.py")], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise ValueError("The website could not be built. Your saved records are unchanged.")
        backup = ROOT / ".editor-backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup.mkdir(parents=True)
        for f in FILES:
            shutil.copy2(ROOT / f, backup / f)
        for f in FILES:
            os.replace(staging / f, ROOT / f)
        for path in (staging / "dist").rglob("*"):
            if path.is_file():
                os.replace(path, ROOT / "dist" / path.relative_to(staging / "dist"))
    return revision()


def command(args, timeout=30):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise ValueError((result.stderr or result.stdout).strip()[-1000:] or "The operation failed.")
    return result.stdout.strip()


def publishing_status():
    global STATUS
    if time.monotonic() - STATUS[0] < 60:
        return STATUS[1]
    status = {"publish_available": bool(shutil.which("git") and shutil.which("gh")), "publish_label": "Save to GitHub", "message": "Saves a backup to the private GitHub repository. Public hosting is not enabled yet."}
    if status["publish_available"]:
        try:
            command(["gh", "api", f"repos/{REPO}", "--jq", ".permissions.push"], timeout=10)
            page = json.loads(command(["gh", "api", f"repos/{REPO}/pages"], timeout=10))
            enabled = command(["gh", "variable", "get", "PAGES_ENABLED", "--repo", REPO], timeout=10)
            if page.get("build_type") == "workflow" and enabled == "true":
                status.update(publish_label="Publish website", message="Saves to GitHub and starts automatic publication. The update normally takes a few minutes.")
        except (ValueError, subprocess.TimeoutExpired):
            pass
    else:
        status["message"] = "Local editing works. Install Git and sign in to GitHub CLI to save updates to GitHub."
    STATUS = (time.monotonic(), status)
    return status


def publish_records():
    if command(["git", "branch", "--show-current"]) != "main":
        raise ValueError("Switch the website repository to its main branch before publishing.")
    remote = command(["git", "remote", "get-url", "github"])
    if remote.rstrip("/").removesuffix(".git") not in (f"https://github.com/{REPO}", f"git@github.com:{REPO}"):
        raise ValueError("The GitHub destination differs from the configured website repository.")
    command([sys.executable, "build.py"])
    paths = list(FILES) + [str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "dist").glob("*.html")] + ["dist/assets/line-motif.svg"]
    command(["git", "add", "--", *paths])
    if command(["git", "diff", "--cached", "--name-only", "--", *paths]):
        command(["git", "commit", "--only", "-m", "Update academic website records", "--", *paths])
    command(["git", "push", "github", "main"], timeout=90)
    if publishing_status()["publish_label"] == "Publish website":
        return "Saved to GitHub. Automatic publication has started; check GitHub Actions for completion."
    return "Saved to GitHub. The online preview must still be published through Codex until public hosting is enabled."


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "editor"), **kwargs)

    def log_message(self, *_):
        pass

    def allowed_host(self):
        return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

    def authenticated(self):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get("Cookie", ""))
            return secrets.compare_digest(cookies["editor_session"].value, SESSION)
        except (KeyError, ValueError):
            return False

    def reply(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "frame-ancestors 'none'")
        super().end_headers()

    def do_GET(self):
        if not self.allowed_host():
            return self.reply(403, {"message": "Open the editor using its 127.0.0.1 address."})
        route = urlparse(self.path).path
        if route.startswith("/api/"):
            if not self.authenticated():
                return self.reply(403, {"message": "Open the editor homepage first."})
            if route == "/api/content":
                with LOCK:
                    return self.reply(200, load_records())
            if route == "/api/status":
                return self.reply(200, publishing_status())
            return self.reply(404, {"message": "Unknown operation."})
        if route == "/":
            body = (ROOT / "editor" / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Set-Cookie", f"editor_session={SESSION}; HttpOnly; SameSite=Strict; Path=/")
            self.end_headers()
            return self.wfile.write(body)
        if route.startswith("/preview/"):
            self.directory = str(ROOT / "dist")
            self.path = self.path[len("/preview"):]
        elif route.startswith("/editor/"):
            self.path = self.path[len("/editor"):]
        return super().do_GET()

    def do_POST(self):
        origin = f"http://127.0.0.1:{self.server.server_port}"
        if not self.allowed_host() or not self.authenticated() or self.headers.get("Origin") != origin:
            return self.reply(403, {"message": "Save requests must come from this editor."})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 <= size <= 2_000_000:
                return self.reply(413, {"message": "The submitted content is too large."})
            body = self.rfile.read(size)
            with LOCK:
                if self.path == "/api/save":
                    rev = save_records(json.loads(body))
                    return self.reply(200, {"ok": True, "message": "Saved locally. The website preview is ready.", "revision": rev})
                if self.path == "/api/publish":
                    return self.reply(200, {"ok": True, "message": publish_records()})
            return self.reply(404, {"message": "Unknown operation."})
        except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as exc:
            return self.reply(400, {"ok": False, "message": str(exc) or "Unable to save. Check the fields and try again."})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Website editor: {url}\nKeep this window open while editing. Close it to stop.", flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
