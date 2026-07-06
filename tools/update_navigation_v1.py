from pathlib import Path
import re
import shutil
import sys

print("=" * 60)
print(" The Artisan's Ledger")
print(" Navigation Rebuild Tool v1.0")
print("=" * 60)
print()

project = Path(__file__).resolve().parent.parent
index_file = project / "index.html"

if not index_file.exists():
    print("ERROR: index.html not found.")
    sys.exit()

backup = project / "index.before-navigation-rebuild.html"
if not backup.exists():
    shutil.copy2(index_file, backup)
    print(f"Backup created: {backup.name}")
    print()

html = index_file.read_text(encoding="utf-8")

# Remove the old global welcome/stat/progress dashboard above the ledger shell.
html = re.sub(
    r'<div id="app" style="display:none">\s*'
    r'<div class="card advisor">.*?</div></div>\s*'
    r'<div class="topgrid">.*?</div>\s*'
    r'<div class="card"><div class="row"><b>Archive Progress</b>.*?</div></div>',
    '<div id="app" style="display:none">\n',
    html,
    count=1,
    flags=re.DOTALL
)

# Replace main navigation.
html = re.sub(
    r'<nav class="tabs ledgerContents">.*?</nav>',
    '''<nav class="tabs ledgerContents">
<button class="tab active" onclick="showTab('advisor',this)">Aldren</button>
<button class="tab" onclick="showTab('professions',this)">Professions</button>
<button class="tab" onclick="showTab('journal',this)">Character Journal</button>
<button class="tab" onclick="showTab('session',this)">Session</button>
<button class="tab" onclick="showTab('verification',this)">Aldren's Workshop</button>
<button class="tab" onclick="showTab('settings',this)">Settings</button>
<button class="tab" onclick="showTab('saves',this)">Saves</button>
    </nav>''',
    html,
    count=1,
    flags=re.DOTALL
)

# Capture old sections.
advisor = re.search(r'<section id="advisor" class="panel active">.*?</section>', html, re.DOTALL)
plan = re.search(r'<section id="plan" class="panel">.*?</section>', html, re.DOTALL)
ingredients = re.search(r'<section id="ingredients" class="panel">.*?</section>', html, re.DOTALL)
builder = re.search(r'<section id="builder" class="panel">.*?</section>', html, re.DOTALL)

if not all([advisor, plan, ingredients, builder]):
    print("ERROR: Could not find one or more Alchemy sections.")
    sys.exit()

plan_html = plan.group(0).replace('<section id="plan" class="panel">', '<div id="alchemyPlan" class="alchemyPageBlock">').replace('</section>', '</div>')
ingredients_html = ingredients.group(0).replace('<section id="ingredients" class="panel">', '<div id="alchemyReagents" class="alchemyPageBlock">').replace('</section>', '</div>')
builder_html = builder.group(0).replace('<section id="builder" class="panel">', '<div id="alchemyLaboratory" class="alchemyPageBlock">').replace('</section>', '</div>')

new_advisor = '''<section id="advisor" class="panel active">
  <div class="card advisor">
    <h2 id="welcomeLine">Welcome back.</h2>
    <div id="greetingBox" class="recipe"></div>
  </div>

  <div class="card">
    <h2>Aldren's Desk</h2>
    <p class="recipe">
      Your ledger is open, your records are preserved, and Aldren is ready when you are.
    </p>
    <p class="small">
      Choose a chapter from the index to continue your work.
    </p>
    <div class="controls" style="margin-top:14px">
      <button onclick="showTab('professions', document.querySelector('[onclick*=\\'professions\\']'))">Open Professions</button>
      <button class="secondary" onclick="showTab('journal', document.querySelector('[onclick*=\\'journal\\']'))">Open Character Journal</button>
    </div>
  </div>
</section>'''

professions = f'''<section id="professions" class="panel">
  <div class="card">
    <h2>Professions</h2>
    <p class="small">Each profession will become its own chapter in The Artisan's Ledger.</p>
  </div>

  <div class="card advisor">
    <h2>Alchemy</h2>
    <p class="small">Volume I — Alchemy Edition</p>
  </div>

  <div class="topgrid">
    <div class="card"><div class="small">Traits Recorded</div><div id="traitStat" class="stat">0/0</div></div>
    <div class="card"><div class="small">Reagents Complete</div><div id="ingStat" class="stat">0/0</div></div>
    <div class="card"><div class="small">Reagents Owned</div><div id="ownedStat" class="stat">0</div></div>
    <div class="card"><div class="small">Useful Experiments</div><div id="craftStat" class="stat">0</div></div>
  </div>

  <div class="card">
    <div class="row"><b>Alchemy Progress</b><b id="pct">0%</b></div>
    <div class="bar"><div id="fill" class="fill"></div></div>
    <div id="remainingText" class="small" style="margin-top:8px"></div>
  </div>

  <div class="card advisor">
    <h2>Aldren's Recommendation</h2>
    <div id="advisorText" class="recipe"></div>
    <div class="controls" style="margin-top:12px">
      <button class="good" onclick="markBest()">Crafted it — record discovery</button>
      <button class="secondary" onclick="undoLast()">Undo Last Craft</button>
      <button class="secondary" onclick="inventoryOnly=!inventoryOnly;render()">Craftable-only: <span id="invMode">OFF</span></button>
      <button class="secondary" onclick="togglePlayMode()">Game Mode</button>
    </div>
  </div>

  <div class="card">
    <h2>Next 5 Experiments</h2>
    <div id="nextFive"></div>
  </div>

  <div class="card advisor">
    <h2>Inventory Report</h2>
    <div id="aldrenInventoryAlert" class="recipe"></div>
  </div>

  <div class="card advisor">
    <h2>Field Note</h2>
    <div id="fieldNote" class="recipe"></div>
  </div>

  {plan_html}

  {ingredients_html}

  {builder_html}
</section>'''

html = html.replace(advisor.group(0), new_advisor + "\n" + professions)
html = html.replace(plan.group(0), "")
html = html.replace(ingredients.group(0), "")
html = html.replace(builder.group(0), "")

html = html.replace("Archive Verification", "Aldren's Workshop")
html = html.replace("Archivist's Ledger", "Aldren's Workshop")

index_file.write_text(html, encoding="utf-8")

print("SUCCESS")
print()
print("Aldren is now the first page.")
print("Alchemy tracker moved into Professions.")
print("Main navigation simplified.")
print()
print("Refresh with Ctrl + F5.")