from pathlib import Path
import re

project = Path(__file__).resolve().parent.parent
html = (project / "index.html").read_text(encoding="utf-8")

print("Sections found:")
for match in re.finditer(r'<section id="([^"]+)"', html):
    print("-", match.group(1))