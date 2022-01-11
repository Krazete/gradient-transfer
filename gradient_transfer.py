from PIL import Image

def getGradientMap(image, scale=1, justcompare=False):
    gradient = image.resize((scale * image.width, scale * image.height)).convert('RGBA')
    gradienti = gradient.convert('L')

    tally = {}
    for (r, g, b, a), i in zip(gradient.getdata(), gradienti.getdata()):
        tally.setdefault(i, {})
        tally[i].setdefault((r, g, b), 0)
        tally[i][(r, g, b)] += a
    sparsemap = {}
    for i in tally:
        t, h, n, w = 0, 0, 0, 0
        for r, g, b in tally[i]:
            weight = tally[i][(r, g, b)] # weight = 1 works well too
            t += r * weight
            h += g * weight
            n += b * weight
            w += weight
        sparsemap[i] = (int(t / w), int(h / w), int(n / w))
    sparsemap.setdefault(0, (0, 0, 0))
    sparsemap.setdefault(255, (255, 255, 255))

    power = 1 + len(sparsemap) / 4 # 1 - 65
    gradientmap = []
    for i in range(256):
        if i in sparsemap:
            gradientmap.append(sparsemap[i])
        else:
            t, h, n, w = 0, 0, 0, 0
            for j in sparsemap:
                r, g, b = sparsemap[j]
                weight = (255 - abs(j - i)) ** power
                t += r * weight
                h += g * weight
                n += b * weight
                w += weight
            gradientmap.append((int(t / w), int(h / w), int(n / w)))

    if justcompare:
        swatch = Image.new('RGB', (256, 2), (0, 255, 0))
        swatch.putdata(gradientmap)
        for i in sparsemap:
            swatch.putpixel((i, 1), (*sparsemap[i], 255))
        return swatch.resize((256, 256), Image.NEAREST)

    return gradientmap

def applyGradientMap(image, gradientmap, scale=1):
    img = image.resize((scale * image.width, scale * image.height)).convert('RGBA')
    imgi = img.convert('L')

    img.putdata([(*gradientmap[i], a) for (r, g, b, a), i in zip(img.getdata(), imgi.getdata())])
    return img

if __name__ == '__main__':
    pinkmap = getGradientMap(Image.open('./input/GiftIcon_Standard.png'), 2)
    goldmap = getGradientMap(Image.open('./input/GiftIcon_Gold.png'), 2)

    molly = Image.open('./input/molly.png')
    applyGradientMap(molly, pinkmap).save('./output/mollypink.png')
    applyGradientMap(molly, goldmap).save('./output/mollygold.png')

    # applyGradientMap(Image.open('./input/pol.png'), goldmap).save('./output/polgold.png')

    # getGradientMap(Image.open('./input/2x2.png'), 8, justcompare=True) # super sparse test
