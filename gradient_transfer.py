from PIL import Image

def getGradientMap(image, size=None, justcompare=False):
    gradient = image.convert('RGBA')
    if size:
        gradient = gradient.resize(size)
    gradienti = gradient.convert('L')

    tally = {}
    for (r, g, b, a), i in zip(gradient.getdata(), gradienti.getdata()):
        if a > 0:
            tally.setdefault(i, [0, 0, 0, 0])
            tally[i][0] += r * a
            tally[i][1] += g * a
            tally[i][2] += b * a
            tally[i][3] += a

    sparsemap = {}
    for i in tally:
        r, g, b, a = tally[i]
        sparsemap[i] = (int(r / a), int(g / a), int(b / a))
    sparsemap.setdefault(0, (0, 0, 0))
    sparsemap.setdefault(255, (255, 255, 255))

    power = 1 + len(sparsemap) / 4 # 1 - 65
    colormap = []
    for i in range(256):
        if i in sparsemap:
            colormap.append(sparsemap[i])
        else:
            t, h, n, w = 0, 0, 0, 0
            for j in sparsemap:
                r, g, b = sparsemap[j]
                weight = (255 - abs(j - i)) ** power
                t += r * weight
                h += g * weight
                n += b * weight
                w += weight
            colormap.append((int(t / w), int(h / w), int(n / w)))

    if justcompare:
        swatch = Image.new('RGB', (256, 2), (0, 255, 0))
        swatch.putdata(colormap)
        for i in sparsemap:
            swatch.putpixel((i, 1), (*sparsemap[i], 255))
        return swatch.resize((256, 256), Image.NEAREST)

    return colormap

def applyGradientMap(image, colormap, size=None):
    img = image.convert('RGBA')
    if size:
        img = img.resize(size)
    imgi = img.convert('L')

    img.putdata([(*colormap[i], a) for (r, g, b, a), i in zip(img.getdata(), imgi.getdata())])
    return img

if __name__ == '__main__':
    pinkmap = getGradientMap(Image.open('./input/GiftIcon_Standard.png'))
    goldmap = getGradientMap(Image.open('./input/GiftIcon_Gold.png'))

    molly = Image.open('./input/molly.png')
    applyGradientMap(molly, pinkmap).save('./output/mollypink.png')
    applyGradientMap(molly, goldmap).save('./output/mollygold.png')

    # applyGradientMap(Image.open('./input/pol.png'), goldmap).save('./output/polgold.png')

    # getGradientMap(Image.open('./input/2x2.png'), (16, 16), justcompare=True) # super sparse test
