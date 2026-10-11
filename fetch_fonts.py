"""Download the publicly served font files used in the design previews."""
from pathlib import Path
import re
from urllib.request import Request, urlopen

root = Path(__file__).parent / "dist" / "assets"
url = "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap"
req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
css = urlopen(req).read().decode()
for i, remote in enumerate(dict.fromkeys(re.findall(r"url\((https:[^)]+)\)", css))):
    extension = ".woff2" if ".woff2" in remote else ".ttf"
    name = f"font-{i}{extension}"
    (root / name).write_bytes(urlopen(remote).read())
    css = css.replace(remote, name)
(root / "fonts.css").write_text(css, encoding="utf-8")
print("Fonts saved locally.")
