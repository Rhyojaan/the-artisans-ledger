from PIL import Image
from collections import deque
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "assets" / "books" / "ledger-cover-v6.png"
out = ROOT / "assets" / "books" / "ledger-cover-clean.png"

img = Image.open(src).convert("RGBA")
w, h = img.size
px = img.load()

# Background is the light tan/gray around the book.
def is_background(r,g,b,a):
    if a == 0:
        return True

    # Remove light tan/gray background from edges
    if r > 95 and g > 75 and b > 50 and (r - b) < 95:
        return True

    # Remove very dark shadow background near edges
    if r < 35 and g < 35 and b < 35:
        return True

    return False

q = deque()
seen = set()

for x in range(w):
    q.append((x,0))
    q.append((x,h-1))
for y in range(h):
    q.append((0,y))
    q.append((w-1,y))

while q:
    x,y = q.popleft()
    if (x,y) in seen or x < 0 or y < 0 or x >= w or y >= h:
        continue

    seen.add((x,y))
    r,g,b,a = px[x,y]

    if is_background(r,g,b,a):
        px[x,y] = (r,g,b,0)
        q.extend([(x+1,y),(x-1,y),(x,y+1),(x,y-1)])

# Clean faint leftovers
for y in range(h):
    for x in range(w):
        r,g,b,a = px[x,y]
        if a > 0 and is_background(r,g,b,a):
            px[x,y] = (r,g,b,0)

img.save(out)
print("Created:", out)
