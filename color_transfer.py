from PIL import Image

class ColorMap:
    def __init__(self):
        self.tally = {}
        self.sparsemap = {}
        self.memomap = {}

    def addMultiple(self, pairs, size=None):
        for image0, image1 in pairs:
            self.add(image0, image1, size, False)
        self.createMaps()

    def add(self, image0, image1, size=None, resetMaps=True):
        original = image0.convert('RGBA')
        recolor = image1.convert('RGBA')
        if size:
            original = original.resize(size)
            recolor = recolor.resize(size)

        assert original.size == recolor.size, 'images differ in size'

        for (r, g, b, a), (t, h, n, s) in zip(original.getdata(), recolor.getdata()):
            c = min(a, s)
            self.tally.setdefault((r, g, b), [0, 0, 0, 0])
            self.tally[(r, g, b)][0] += t * c
            self.tally[(r, g, b)][1] += h * c
            self.tally[(r, g, b)][2] += n * c
            self.tally[(r, g, b)][3] += c

        if resetMaps:
            self.createMaps()

    def createMaps(self):
        self.sparsemap = {}
        for r, g, b in self.tally:
            t, h, n, c = self.tally[(r, g, b)]
            self.sparsemap[(r, g, b)] = (int(t / c), int(h / c), int(n / c))
        self.sparsemap.setdefault((0, 0, 0), (0, 0, 0))
        self.sparsemap.setdefault((255, 255, 255), (255, 255, 255))

        power = 1 + len(self.sparsemap) / 262144
        self.memomap = self.sparsemap.copy()

    def getColor(self, r, g, b):
        if (r, g, b) not in self.memomap:
            u, k, l, w = 0, 0, 0, 1
            for t, h, n in self.sparsemap: # todo: optimize this loop
                y, j, m = self.sparsemap[(t, h, n)]
                weight = ((255 - abs(t - r)) ** 2 + (255 - abs(h - g)) ** 2 + (255 - abs(n - b)) ** 2) ** 100
                u += y * weight
                k += j * weight
                l += m * weight
                w += weight
            self.memomap[(r, g, b)] = (int(u / w), int(k / w), int (l / w))
        return self.memomap[(r, g, b)]

    def applyColormap(self, image, size=None):
        img = image.convert()
        if size:
            img = img.resize(size)

        img.putdata([(*self.getColor(r, g, b), a) for r, g, b, a in img.getdata()])
        return img

if __name__ == '__main__':
    cm = ColorMap()
    cm.addMultiple([
        (Image.open('./ai/unit_model_804_02_face_texture.png'), Image.open('./ai/unit_model_804_03_face_texture.png')),
        (Image.open('./ai/unit_model_804_02_texture.png'), Image.open('./ai/unit_model_804_03_texture.png'))
    ], (64, 64))
    len(cm.memomap)

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
    #     img = cm.applyColormap(Image.open('./ai/{}.png'.format(png)), (256, 256)).save('./ai2/{}.png'.format(png))

import time
t0 = time.time()
im = cm.applyColormap(Image.open('./ai/fight.png'))
print(time.time() - t0)
im.save('./ai2/fight.png')

s = -int(-len(cc.memomap) ** 0.5 // 1)
j = Image.new('RGB', (s, s))
j.putdata(list(cc.memomap.keys()))
j.resize((1024, 1024), Image.NEAREST).save('ai2/cm0.png')
k = Image.new('RGB', (s, s))
k.putdata(list(cc.memomap.values()))
k.resize((1024, 1024), Image.NEAREST).save('ai2/cm1.png')
