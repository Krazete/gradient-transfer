import time
from PIL import Image
import math

c = 64
k = int(256 / c)

# store colors as numbers
t0 = time.time()
z = {}
for r in range(c):
    for g in range(c):
        for b in range(c):
            z[c ** 2 * r + c * g + b] = c ** 2 * r * k + c * g * k + b * k
t1 = time.time()
print(1000 * (t1 - t0))

# store colors as triples
t0 = time.time()
z = {}
for r in range(c):
    for g in range(c):
        for b in range(c):
            z[(r, g, b)] = (r * k, g * k, b * k)
t1 = time.time()
print(1000 * (t1 - t0))

# store colors as pixels
t0 = time.time()
s = math.ceil(c ** 1.5)
z = Image.new('RGB', (s, s))
i = 0
for r in range(c):
    for g in range(c):
        for b in range(c):
            x = i % s
            y = i // s
            z.putpixel((x, y), (r * k, g * k, b * k))
            i += 1
t1 = time.time()
print(1000 * (t1 - t0))
