import time
from PIL import Image

d = 7 # color depth [0 - 8]

c = 2 ** d
m = int(256 / c)

t0 = time.time()
z = {}
for r in range(c):
    for g in range(c):
        for b in range(c):
            i = c ** 2 * r + c * g + b
            z[i] = m * i
t1 = time.time()
print('storing colors as numbers: {:6.3f}s'.format(t1 - t0))

t0 = time.time()
z = {}
for r in range(c):
    for g in range(c):
        for b in range(c):
            z[(r, g, b)] = (m * r, m * g, m * b)
t1 = time.time()
print('storing colors as triples: {:6.3f}s'.format(t1 - t0)) # best

t0 = time.time()
z = Image.new('RGB', (c ** 3, 1))
for r in range(c):
    for g in range(c):
        for b in range(c):
            i = c ** 2 * r + c * g + b
            z.putpixel((i, 0), (m * r, m * g, m * b))
# cannot use putdata since colors would be sparse and unsorted in practice
t1 = time.time()
print('storing colors as pixels:  {:6.3f}s'.format(t1 - t0)) # worst

t0 = time.time()
z = []
for r in range(c):
    for g in range(c):
        for b in range(c):
            z.append(((r, g, b), (m * r, m * g, m * b)))
t1 = time.time()
print('storing colors as pairs:   {:6.3f}s'.format(t1 - t0))
