from pathlib import Path

p = Path("index.html")
html = p.read_text(encoding="utf-8")

html = html.replace("Archive Verification", "Aldren's Workshop")
html = html.replace("Archive Verification & Feedback", "Aldren's Workshop")

p.write_text(html, encoding="utf-8")

print("Done!")
