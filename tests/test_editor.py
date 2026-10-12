"""Regression checks for local editing, using disposable website copies only."""
from __future__ import annotations

from copy import deepcopy
from html import escape
from html.parser import HTMLParser
from http.client import HTTPConnection
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SPEC = importlib.util.spec_from_file_location("website_editor_under_test", SOURCE / "edit.py")
editor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(editor)


class Links(HTMLParser):
    def __init__(self, value):
        super().__init__(convert_charrefs=True)
        self.urls = []
        self.text = []
        self.feed(value)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.urls.append(dict(attrs)["href"])

    def handle_data(self, data):
        self.text.append(data)


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="academic-editor-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # Stable records keep tests independent of future edits to the live site.
        for name in editor.FILES:
            shutil.copy2(FIXTURES / name, self.root / name)
        shutil.copy2(SOURCE / "build.py", self.root / "build.py")
        (self.root / "dist" / "assets").mkdir(parents=True)
        (self.root / "dist" / "index.html").write_text("Existing preview", encoding="utf-8")
        (self.root / "dist" / "assets" / "fixture.txt").write_text("Existing asset", encoding="utf-8")
        (self.root / "editor").mkdir()
        (self.root / "editor" / "index.html").write_text("Editor homepage", encoding="utf-8")
        self.root_patch = patch.object(editor, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def snapshot(self):
        return {
            str(path.relative_to(self.root)): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file() and path.name != "build.py"
        }

    def content(self):
        return json.loads((self.root / "content.json").read_text(encoding="utf-8"))


class RecordsTests(FixtureCase):
    def test_unchanged_roundtrip_preserves_every_file_byte_for_byte(self):
        before = self.snapshot()
        payload = editor.load_records()
        with patch.object(editor.subprocess, "run") as run:
            revision = editor.save_records(payload)
        self.assertEqual(revision, payload["revision"])
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / ".editor-backups").exists())
        run.assert_not_called()

    def test_edit_preserves_existing_links_unicode_and_complete_records(self):
        original = self.content()
        papers = json.loads((self.root / "publications.json").read_text(encoding="utf-8"))
        payload = editor.load_records()
        old_revision = payload["revision"]
        suffix = " New result by José — [Dataset](https://example.org/data?lang=fil&version=2)."
        old_links = Links(original["about"][1]).urls
        payload["content"]["about"][1] += suffix
        editor.save_records(payload)
        stored = self.content()
        expected = deepcopy(original)
        expected["about"][1] = stored["about"][1]
        self.assertEqual(stored, expected)
        self.assertEqual(
            Links(stored["about"][1]).urls,
            old_links + ["https://example.org/data?lang=fil&version=2"],
        )
        self.assertEqual(editor.editable(stored["about"][1]), payload["content"]["about"][1])
        self.assertEqual(json.loads((self.root / "publications.json").read_text(encoding="utf-8")), papers)
        self.assertNotEqual(editor.revision(), old_revision)
        backups = list((self.root / ".editor-backups").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual(json.loads((backups[0] / "content.json").read_text(encoding="utf-8")), original)
        page = (self.root / "dist" / "index.html").read_text(encoding="utf-8")
        for paper in papers:
            self.assertIn(escape(paper["title"]), page)
            for author in paper["authors"].split(", "):
                if "Joseph Marvin Imperial" not in author:
                    self.assertIn(escape(author), page)
        self.assertIn("José", page)

    def test_publication_edit_retains_full_author_list_and_other_papers(self):
        payload = editor.load_records()
        original = deepcopy(payload["publications"])
        index = max(range(len(original)), key=lambda i: len(original[i]["authors"]))
        payload["publications"][index]["authors"] += ", Zoë Muñoz"
        payload["publications"][index]["title"] += " — Updated"
        payload["publications"][index]["featured"] = True
        editor.save_records(payload)
        stored = editor.load_records()["publications"]
        self.assertEqual(stored, payload["publications"])
        for i, paper in enumerate(original):
            if i != index:
                self.assertEqual(stored[i], paper)
        page = (self.root / "dist" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Zoë Muñoz", page)
        self.assertIn("paper-featured", page)

    def test_adjacent_rich_links_keep_separate_destinations(self):
        text = "[First](https://example.org/a),[Second](https://example.org/b)"
        value = editor.rich_html(text)
        self.assertEqual(Links(value).urls, ["https://example.org/a", "https://example.org/b"])
        self.assertEqual("".join(Links(value).text), "First,Second")

    def test_rich_link_destination_retains_balanced_parentheses(self):
        text = "See [Topic](https://example.org/wiki/Topic_(research)), then [Data](https://example.org/data)."
        value = editor.rich_html(text)
        self.assertEqual(Links(value).urls, ["https://example.org/wiki/Topic_(research)", "https://example.org/data"])
        self.assertEqual(editor.editable(value), text)

    def test_raw_html_in_edited_text_is_escaped(self):
        value = editor.rich_html('<script>alert("x")</script> & [Safe](https://example.org/)')
        self.assertNotIn("<script>", value)
        self.assertIn("&lt;script&gt;", value)
        self.assertEqual(Links(value).urls, ["https://example.org/"])

    def test_unsafe_structured_urls_are_refused_without_changing_files(self):
        before = self.snapshot()
        for url in ("javascript:alert(1)", "data:text/html,test", "file:///tmp/test", "//example.org", "https://exa mple.org"):
            for location in ("site", "social", "publication"):
                with self.subTest(url=url, location=location):
                    payload = editor.load_records()
                    if location == "site":
                        payload["content"]["site"]["scholar_url"] = url
                    elif location == "social":
                        payload["content"]["socials"][0]["url"] = url
                    else:
                        payload["publications"][0]["url"] = url
                    with self.assertRaises(ValueError):
                        editor.save_records(payload)
                    self.assertEqual(self.snapshot(), before)

    def test_stale_revision_refuses_overwrite_of_newer_records(self):
        payload = editor.load_records()
        payload["content"]["news"].insert(0, "Older window update")
        content = self.content()
        content["news"].insert(0, "Newer independently saved update")
        (self.root / "content.json").write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "changed in another window"):
            editor.save_records(payload)
        self.assertEqual(self.snapshot(), before)

    def test_failed_build_leaves_records_and_preview_unchanged(self):
        (self.root / "build.py").write_text("raise SystemExit(7)\n", encoding="utf-8")
        payload = editor.load_records()
        payload["content"]["news"].insert(0, "A change that cannot be built")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "could not be built"):
            editor.save_records(payload)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / ".editor-backups").exists())
        self.assertFalse(list(self.root.glob(".editor-build-*")))

    def test_duplicated_social_and_profile_urls_remain_consistent(self):
        for field, label in (("scholar_url", "Google Scholar"), ("cv_url", "CV"), ("github_url", "Github"), ("anthology_url", "ACL Anthology")):
            with self.subTest(field=field, edited="social"):
                payload = editor.load_records()
                social = next(row for row in payload["content"]["socials"] if row["label"] == label)
                social["url"] = "https://example.org/from-social/" + field
                editor.save_records(payload)
                self.assertEqual(self.content()["site"][field], social["url"])
            with self.subTest(field=field, edited="profile"):
                payload = editor.load_records()
                url = "https://example.org/from-profile/" + field
                payload["content"]["site"][field] = url
                editor.save_records(payload)
                social = next(row for row in self.content()["socials"] if row["label"] == label)
                self.assertEqual(social["url"], url)


class HttpTests(FixtureCase):
    def setUp(self):
        super().setUp()
        self.server = editor.ThreadingHTTPServer(("127.0.0.1", 0), editor.Handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.host = f"127.0.0.1:{self.server.server_port}"
        self.origin = "http://" + self.host
        self.cookie = "editor_session=" + editor.SESSION

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def request(self, method, path, data=None, headers=None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            body = None if data is None else json.dumps(data).encode("utf-8")
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_homepage_establishes_http_only_strict_session_and_api_requires_it(self):
        status, headers, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertEqual(body, b"Editor homepage")
        self.assertIn("HttpOnly", headers["Set-Cookie"])
        self.assertIn("SameSite=Strict", headers["Set-Cookie"])
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertEqual(self.request("GET", "/api/content")[0], 403)
        status, _, body = self.request("GET", "/api/content", headers={"Cookie": self.cookie})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), editor.load_records())

    def test_host_check_rejects_rebound_hostname(self):
        for path in ("/", "/api/content", "/preview/index.html"):
            with self.subTest(path=path):
                status, _, _ = self.request("GET", path, headers={"Host": "attacker.example", "Cookie": self.cookie})
                self.assertEqual(status, 403)

    def test_save_requires_matching_host_origin_and_session(self):
        payload = editor.load_records()
        before = self.snapshot()
        valid = {"Host": self.host, "Origin": self.origin, "Cookie": self.cookie, "Content-Type": "application/json"}
        bad_headers = [
            {**valid, "Host": "attacker.example"},
            {**valid, "Origin": "https://attacker.example"},
            {**valid, "Origin": "null"},
            {key: value for key, value in valid.items() if key != "Origin"},
            {**valid, "Cookie": "editor_session=incorrect"},
            {key: value for key, value in valid.items() if key != "Cookie"},
        ]
        for headers in bad_headers:
            with self.subTest(headers=list(headers)):
                # Rejection happens before the body is read. An empty body avoids
                # Windows resetting a socket that still contains rejected data.
                status, _, _ = self.request("POST", "/api/save", headers=headers)
                self.assertEqual(status, 403)
                self.assertEqual(self.snapshot(), before)
        status, _, body = self.request("POST", "/api/save", payload, valid)
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["ok"])
        self.assertEqual(json.loads(body)["revision"], payload["revision"])
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
