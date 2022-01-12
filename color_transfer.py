from PIL import Image

class ColorMap:
    def __init__(self):
        self.tally = {}
        self.sparsemap = {}
        self.memomap = {}

    def addMultiple(self, pairs, scale=1):
        for image0, image1 in pairs:
            self.add(image0, image1, scale, False)
        self.createMaps()

    def add(self, image0, image1, scale=1, resetMaps=True):
        original = image0.resize((int(scale * image0.width), int(scale * image0.height))).convert('RGBA')
        recolor = image1.resize((int(scale * image1.width), int(scale * image1.height))).convert('RGBA')

        assert original.size == recolor.size, 'images differ in size'

        for (r, g, b, a), (t, h, n, s) in zip(original.getdata(), recolor.getdata()):
            self.tally.setdefault((r, g, b), {})
            self.tally[(r, g, b)].setdefault((t, h, n), 0)
            self.tally[(r, g, b)][(t, h, n)] += min(a, s)

        if resetMaps:
            self.createMaps()

    def createMaps(self):
        self.sparsemap = {}
        for r, g, b in self.tally:
            y, j, m, w = 0, 0, 0, 0
            for t, h, n in self.tally[(r, g, b)]:
                weight = self.tally[(r, g, b)][(t, h, n)] # lower is smoother
                y += t * weight
                j += h * weight
                m += n * weight
                w += weight
            self.sparsemap[(r, g, b)] = (int(y / w), int(j / w), int(m / w))
        self.sparsemap.setdefault((0, 0, 0), (0, 0, 0))
        self.sparsemap.setdefault((255, 255, 255), (255, 255, 255))

        self.memomap = self.sparsemap.copy()

    def getColor0(self, r, g, b): # 20 minutes
        if (r, g, b) not in self.memomap:
            u, k, l, w = 0, 0, 0, 0
            for t, h, n in self.sparsemap:
                y, j, m = self.sparsemap[(t, h, n)]
                weight = (765 - abs(t - r) - abs(h - g) - abs(n - b)) ** 128
                u += y * weight
                k += j * weight
                l += m * weight
                w += weight
            w = max(1, w)
            self.memomap[(r, g, b)] = (int(u / w), int(k / w), int (l / w))
        return self.memomap[(r, g, b)]

    def getColor1(self, r, g, b): # 13 minutes
        if (r, g, b) not in self.memomap:
            distancemap = {}
            for t, h, n in self.sparsemap:
                d = abs(t - r) + abs(h - g) + abs(n - b) # manhattan distance
                distancemap.setdefault(d, [])
                distancemap[d].append((t, h, n))
            distances = list(distancemap)
            distances.sort()
            u, k, l, w = 0, 0, 0, 0
            for d in distances[:16]:
                for t, h, n in distancemap[d]:
                    y, j, m = self.sparsemap[(t, h, n)]
                    u += y
                    k += j
                    l += m
                    w += 1
            w = max(1, w)
            self.memomap[(r, g, b)] = (int(u / w), int(k / w), int (l / w))
        return self.memomap[(r, g, b)]

    def getColor2(self, r, g, b): # 12 minutes
        if (r, g, b) not in self.memomap:
            distances = sorted(self.sparsemap, key=lambda rgb: abs(rgb[0] - r) + abs(rgb[1] - g) + abs(rgb[2] - b))
            u, k, l, w = 0, 0, 0, 0
            for t, h, n in distances[:len(distances) // 100]:
                y, j, m = self.sparsemap[(t, h, n)]
                u += y
                k += j
                l += m
                w += 1
            w = max(1, w)
            self.memomap[(r, g, b)] = (int(u / w), int(k / w), int (l / w))
        return self.memomap[(r, g, b)]

    def applyColorMap(self, image, scale=1, method=1):
        img = image.resize((int(scale * image.width), int(scale * image.height))).convert('RGBA')

        getColor = [self.getColor0, self.getColor1, self.getColor2][method]
        img.putdata([(*getColor(r, g, b), a) for r, g, b, a in img.getdata()])
        return img

    def dumpSparseMap(self):
        s = -int(-len(self.sparsemap) ** 0.5 // 1)
        original = Image.new('RGBA', (s, s))
        original.putdata(list(self.sparsemap))
        recolor = Image.new('RGBA', (s, s))
        recolor.putdata(list(self.sparsemap.values()))
        return original, recolor

    def dumpMemoMap(self):
        s = -int(-len(self.memomap) ** 0.5 // 1)
        original = Image.new('RGBA', (s, s))
        original.putdata(list(self.memomap))
        recolor = Image.new('RGBA', (s, s))
        recolor.putdata(list(self.memomap.values()))
        return original, recolor

if __name__ == '__main__':
    cm = ColorMap()
    cm.addMultiple([
        (Image.open('./input/ai/unit_model_804_02_face_texture.png'), Image.open('./input/ai/unit_model_804_03_face_texture.png')),
        (Image.open('./input/ai/unit_model_804_02_texture.png'), Image.open('./input/ai/unit_model_804_03_texture.png'))
    ], 0.1)

    # pngs = [
    #     'CHaiA_body_dff_4k',
    #     'CHaiA_extraFaceParts_dff_4k',
    #     'CHaiA_eye_dff_4k',
    #     'CHaiA_eyeHighlight_dff_4k',
    #     'CHaiA_face_dff_4k_mask',
    #     'CHaiA_face_dff_4k',
    #     'CHaiA_hand_dff_4k',
    #     'CHaiA_mouth_dff_4k',
    #     'CHaiA_pants_dff_4k',
    #     'CHaiA_pyokopyoko_dff_4k',
    #     'CHaiA_upCloth_dff_4k',
    #     'hair1',
    #     'hair2'
    # ]
    #
    # for png in pngs:
    #     img = cm.applyColorMap(Image.open('./input/ai/{}.png'.format(png)), (256, 256)).save('./output/ai/{}.png'.format(png))

import time

t0 = time.time()
im = cm.applyColorMap(Image.open('./input/ai/azur.png'), method=0)
print(time.time() - t0)
im.save('./output/ai/azur0.png')
cm.createMaps()

t0 = time.time()
im = cm.applyColorMap(Image.open('./input/ai/azur.png'), method=1)
print(time.time() - t0)
im.save('./output/ai/azur1.png')
cm.createMaps()

t0 = time.time()
im = cm.applyColorMap(Image.open('./input/ai/azur.png'), method=2)
print(time.time() - t0)
im.save('./output/ai/azur2.png')
cm.createMaps()
