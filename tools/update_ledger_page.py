from pathlib import Path
import re
import shutil
import sys

print("=" * 60)
print(" The Artisan's Ledger")
print(" Ledger Theme Updater v2.0")
print("=" * 60)
print()

project = Path(__file__).resolve().parent.parent

style_file = project / "style.css"

page_image = project / "assets/pages/ledger-page-v1.png"
desk_image = project / "assets/backgrounds/desk-background-v1.png"

if not style_file.exists():
    print("ERROR: style.css not found.")
    sys.exit()

if not page_image.exists():
    print("ERROR: ledger-page-v1.png not found.")
    sys.exit()

if not desk_image.exists():
    print("ERROR: desk-background-v1.png not found.")
    sys.exit()

backup = project / "style.before-theme-update.css"

if not backup.exists():
    shutil.copy2(style_file, backup)
    print(f"Backup created: {backup.name}")
    print()

css = style_file.read_text(encoding="utf-8")

# ----------------------------------------------------
# BODY
# ----------------------------------------------------

body_pattern = re.compile(
    r"body\s*\{.*?\}",
    re.DOTALL
)

body_replace = """
body{

    margin:0;

    background-image:url("assets/backgrounds/desk-background-v1.png");
    background-size:cover;
    background-position:center;
    background-attachment:fixed;
    background-repeat:no-repeat;

    color:#3b2414;

    overflow-x:hidden;
}
"""

css = body_pattern.sub(body_replace, css, count=1)

# ----------------------------------------------------
# LEDGER PAGE
# ----------------------------------------------------

page_pattern = re.compile(
    r"\.ledgerPages\s*\{.*?\}",
    re.DOTALL
)

page_replace = """
.ledgerPages{

    width:min(920px,94vw);

    min-height:1450px;

    margin:50px auto;

    padding:110px 95px 150px;

    background-image:url("assets/pages/ledger-page-v1.png");

    background-size:100% 100%;

    background-repeat:no-repeat;

    background-position:center top;

    border:none;

    box-shadow:none;

    color:#3b2414;

    position:relative;
}
"""

css = page_pattern.sub(page_replace, css, count=1)

style_file.write_text(css, encoding="utf-8")

print("SUCCESS")
print()
print("Desk background installed.")
print("Ledger page installed.")
print()
print("Refresh with Ctrl + F5.")