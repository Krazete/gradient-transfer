from gradient_transfer import getGradientMap, applyGradientMap
from PIL import Image, ImageMath

pngs = [
    'Cerebella_Portrait',
    'Annie_Portrait',
    'Beowulf_Portrait',
    'BigBand_Portrait',
    'Double_Portrait',
    'Eliza_Portrait',
    'Filia_Portrait',
    'Fukua_Portrait',
    'MsFortune_Portrait',
    'Painwheel_Portrait',
    'Parasoul_Portrait',
    'Peacock_Portrait',
    'RoboFortune_Portrait',
    'Squigly_Portrait',
    'Valentine_Portrait'
]

def petrify_sprite(im, spectral_ids=[]): # from gen_moves.py in Krazete/sgmprocessor
    'Return grayscale version of codified sprite, with spectral areas rendered translucent.'
    r = im.getchannel(0) # palette
    g = im.getchannel(1) # linework
    b = im.getchannel(2) # detail

    # mask detail with palette areas and subtract inverted linework
    sprite = ImageMath.eval('convert((r > 0) * b - (0xFF - g), "L")', r=r, g=g, b=b)

    if len(spectral_ids):
        spectral_areas = ' + '.join('(r == {})'.format(id) for id in spectral_ids)
        # create scaled binary mask of palette areas minus spectral areas
        opaque = ImageMath.eval('convert(0xFF * (r > 0) * (1 - (' + spectral_areas + ')), "L")', r=r)
        # mask detail with spectral areas and scale to adjust intensity
        translucent = ImageMath.eval('convert(0xFF * (b * (' + spectral_areas + ') - 0x64) / (0xFF - 0x64), "L")', r=r, b=b)
        # add together opaque mask, translucent mask, and inverted linework
        a = ImageMath.eval('convert(o + t + (0xFF - g), "L")', o=opaque, t=translucent, g=g)
    else:
        # create scaled binary mask of palette areas and add inverted linework
        a = ImageMath.eval('convert(0xFF * (r > 0) + (0xFF - g), "L")', r=r, g=g)

    sprite.putalpha(a)
    return sprite

gradientmap = getGradientMap(Image.open('./input/GiftIcon_Gold.png'), 2)
for png in pngs:
    sprite = petrify_sprite(Image.open('./input/sprite/{}.png'.format(png)).convert('RGBA'), [133])
    gilded = applyGradientMap(sprite, gradientmap)
    gilded.save('./output/gilded/{}.png'.format(png))
