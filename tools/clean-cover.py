from PIL import Image
from collections import deque

src = "assets/books/ledger-cover-v6.png"
out = "assets/books/ledger-cover-clean.png"

img = Image.open(src).convert("RGBA")
w, h = img.size
px = img.load()

# flood remove background from edges
seen = set()
q = deque()

for x in range(w):
    q.append((x,0))
    q.append((x,h-1))
for y in range(h):
    q.append((0,y))
    q.append((w-1,y))

def is_bg(r,g,b,a):
    # light tan/gray background range
    return a > 0 and r > 120 and g > 95 and b > 65 and abs(r-g) < 70

while q:
    x,y = q.popleft()
    if (x,y) in seen or x < 0 or y < 0 or x >= w or y >= h:
        continue
    seen.add((x,y))
    r,g,b,a = px[x,y]
    if is_bg(r,g,b,a):
        px[x,y] = (r,g,b,0)
        q.extend([(x+1,y),(x-1,y),(x,y+1),(x,y-1)])

img.save(out)
print("Created", out)
