# gradient-transfer
An experiment with intensity-based and correspondence-based color transfer.

*Note: This markdown file contains abbreviated code segments. All lines pertaining to the display of runtimes and tables have been removed. Tables have also been modified to improve the layout. For the original version of this document, see README.ipynb.*

*Note 2: The output folder contains a few extra examples which are not included in the README.*

```python
from PIL import Image
from gradient_transfer import getGradientMap, applyGradientMap
from color_transfer import ColorMap
```

## gradient_transfer.py
This takes gradient information from one image and applies it to another based on intensity (grayscale values).

```python
goldgift = Image.open('./input/GiftIcon_Gold.png')
molly = Image.open('./input/molly.png')

goldmap = getGradientMap(goldgift)
goldmolly = applyGradientMap(molly, goldmap)
```

|goldgift|molly|gradient extracted from goldgift|gradient extracted from goldgift applied to molly|
|-|-|-|-|
|<img src="./input/GiftIcon_Gold.png" width="256">|<img src="./input/molly.png" width="256">|<img src="./readme/goldgradient.png">|<img src="./readme/goldmolly.png" width="256">|
|(210×256)|(128×128)|(256×256)|(128×128)|

> Gold-Gift Gradient Map extracted in 0.040 seconds and applied in 0.010 seconds.

Any missing intensity values are filled in by taking a weighted average of the existing intensity values scaled exponentially by similarity (distance in the gradient).

In the first gradient below, the bottom half of the gradient shows missing intensity values as green lines and the top half shows the completed gradient after filling them in from the surrounding colors.

Scaling up the input can also fill in missing values, as shown below in the second gradient. This gives a smoother result too, which yields a better output when applying the gradient to another image.

```python
pinkgift = Image.open('./input/GiftIcon_Standard.png')
greygift = Image.open('./input/GiftIcon_Grey.png')

pinkmap = getGradientMap(pinkgift)
ungrey = applyGradientMap(greygift, pinkmap)
pinkmap2 = getGradientMap(pinkgift, 2)
ungrey2 = applyGradientMap(greygift, pinkmap2)
```

|pinkgift|greygift|gradient extracted from pinkgift|gradient extracted from pinkgift applied to greygift|gradient extracted from pinkgift×2|gradient extracted from pinkgift×2 applied to greygift|
|-|-|-|-|-|-|
|<img src="./input/GiftIcon_Standard.png" width="256">|<img src="./input/GiftIcon_Grey.png" width="256">|<img src="./readme/pinkgradient.png">|<img src="./readme/ungrey.png" width="256">|<img src="./readme/pinkgradient2.png">|<img src="./readme/ungrey2.png" width="256">
|(210×256)|(210×256)|(256×256)|(210×256)|(256×256)|(210×256)|

> Pink-Gift Gradient Map extracted in 0.050 seconds and applied in 0.065 seconds.  
> Scaled-Up-Pink-Gift Gradient Map extracted in 0.149 seconds and applied in 0.025 seconds.

Since there are only 256 intensity values, inputs with larger image dimensions should affect the execution time of gradient extraction and application by a few seconds at most. The runtime scales linearly, proportional to the number of pixels in the image.

```python
pol = Image.open('./input/pol.png')

polmap = getGradientMap(pol)
polpol = applyGradientMap(pol, polmap)
```

|pol|gradient extracted from pol|gradient extracted from pol applied to pol|
|-|-|-|
|<img src="./input/pol.png" width="512">|<img src="./readme/polgradient.png">|<img src="./readme/polpol.png" width="512">|
|(3061×3061)|(256×256)|(3061×3061)|

> Polka Gradient Map extracted in 4.729 seconds and applied in 5.174 seconds.

## color_transfer.py
This takes two color variations of an image to create a correspondence mapping that can be applied to similarly colored images.

```python
kface = Image.open('./input/ai/unit_model_804_02_face_texture.png')
kbody = Image.open('./input/ai/unit_model_804_02_texture.png')
bface = Image.open('./input/ai/unit_model_804_03_face_texture.png')
bbody = Image.open('./input/ai/unit_model_804_03_texture.png')

k2b = ColorMap()
k2b.addMultiple([(kface, bface), (kbody, bbody)])
b2k = ColorMap()
b2k.addMultiple([(bface, kface), (bbody, kbody)])
```

|kface|kbody|bface|bbody|
|-|-|-|-|
|<img src="./input/ai/unit_model_804_02_face_texture.png">|<img src="./input/ai/unit_model_804_02_texture.png">|<img src="./input/ai/unit_model_804_03_face_texture.png">|<img src="./input/ai/unit_model_804_03_texture.png">|
|(512×512)|(512×512)|(512×512)|(512×512)|

|all colors in kface+kbody|colors in bface+bbody corresponding to kface+kbody|all colors in bface+bbody|colors in kface+kbody corresponding to bface+bbody|
|-|-|-|-|
|<img src="./readme/k2bmapk.png" width="256">|<img src="./readme/k2bmapb.png" width="256">|<img src="./readme/b2kmapb.png" width="256">|<img src="./readme/b2kmapk.png" width="256">|
|(8219 pixels)|(8219 pixels)|(4309 pixels)|(4309 pixels)|

> Kizuna-AI-to-Black-AI Color Map (k2b) initialized in 0.783 seconds.  
> Black-AI-to-Kizuna-AI Color Map (b2k) initialized in 0.696 seconds.

With the large amount of time it takes to apply a color map, it's a good idea to check quality before proceeding. To do so, simply apply the color map to its reference image(s) and compare. This is the quickest way since there aren't any new colors to calculate; it's a mere dictionary call for every pixel.

The results below for k2b look decent, but b2k does not. Although disappointing, it would be better to abandon b2k now.

```python
k2bface = k2b.apply(kface)
k2bbody = k2b.apply(kbody)
b2kface = b2k.apply(bface)
b2kbody = b2k.apply(bbody)
```

|k2b applied to kface|k2b applied to kbody|b2k applied to bface|b2k applied to bbody|
|-|-|-|-|
|<img src="./readme/k2bface.png">|<img src="./readme/k2bbody.png">|<img src="./readme/b2kface.png">|<img src="./readme/b2kbody.png">|
|(512×512)|(512×512)|(512×512)|(512×512)|

> Two k2b and two b2k applications performed in 0.807 seconds.

Unlike gradient_transfer.py which has just 256 intensity values to store, color_transfer.py has to deal with 256³ = 16,777,216 possible color values.

Calculating the mapping of a new color thus takes a lot of time, so missing values are not immediately filled in on initialization. Color values are instead calculated and memoized as needed whenever the color map is applied. Note below how the amount of stored color correspondences increase in k2b and b2k.

(Also note how terrible b2k is, as predicted earlier. b2k will not be used in any further examples.)

```python
artist = Image.open('./input/ai/artistprofile.png')
melty = Image.open('./input/ai/meltyworld.png')

k2bartist = k2b.apply(artist, 0.27)
b2kmelty = b2k.apply(melty, 0.375)
```

|artist|k2b applied to artist|melty|b2k applied to melty|
|-|-|-|-|
|<img src="./input/ai/artistprofile.png" width="216">|<img src="./readme/k2bartist.png">|<img src="./input/ai/meltyworld.png" width="216">|<img src="./readme/b2kmelty.png">|
|(800×1000)|(216×270)|(576×720)|(216×270)|

|colors in kface+kbody plus artist|colors in bface+bbody plus colors mapped from artist|colors in bface+bbody plus melty|colors in kface+kbody plus colors mapped from melty|
|-|-|-|-|
|<img src="./readme/k2bmapk2.png" width="256">|<img src="./readme/k2bmapb2.png" width="256">|<img src="./readme/b2kmapb2.png" width="256">|<img src="./readme/b2kmapk2.png" width="256">|
|(40689 pixels)|(40689 pixels)|(25535 pixels)|(25535 pixels)|

> k2b applied in 186.589 seconds.  
> b2k applied in 59.299 seconds.

I went through several iterations to try to reduce the amount of time needed to estimate a color mapping. These are available upon application as methods 0-4.

|Method|0|1|2|3|4|
|-|-|-|-|-|-|
|Speed|★☆☆☆☆|★★★☆☆|★★★★☆|★★★★★|★★★★★|
|Quality|★★★★☆|★★★★★|★★★★★|★★★☆☆|★☆☆☆☆|

Method 0 copies exactly what gradient_transfer.py does, calculating a weighted average from all of the initialized colors scaled exponentially by similarity. As expected, this method takes the longest to execute.

Method 1 groups the initialized colors by their similarity to the input color, sorts them to find the closest 16 groups, and calculates an average from those groups' colors. Even though this requires an additional dictionary and sorted array, it takes a lot less time than method 0. The quality is consistent and often better than method 0, so this is the default method.

Method 2 attempts to hasten method 1 by forgoing the dictionary. It sorts the initialized colors by similarity and  calculates an average from the top 100th of them. It is a little faster, but the lack of groupings means a lack of consistency with the last part of that 100th. This shouldn't matter too much with a large amount of initialized colors though.

Method 3 does what method 0 does, but only includes initialized colors with a similarity of 16 or better. If there are none, it reruns with a doubled similarity threshhold. This is the fastest method since it doesn't rely on extra dictionaries or arrays or sorting. It also typically yields quality comparable to method 0 since the weight formula gives dissimilar colors such a small weight anyway.

Method 4 tries to do what method 3 does without ever needing to rerun and without the costly weight formula. During the loop, it remembers the closest color and accumulates other colors if they are of a similarity of 16 or better from that color. Whenever it runs into a color that is closer to the input color than the currently remembered closest color, it resets the accumlation and continues on with the new closest color. After the loop ends, it averages the accumulated colors. This method is about the same speed as method 3 and the resulting output isn't as good, so this method is not recommended.

```python
terr = Image.open('./input/ai/terribleautotranslation.png')
ap19 = Image.open('./input/ai/aiparty2019.png')

for img in [terr, ap19]:
    scale = 300 / min(img.size)
    for method in range(5):
        k2b.initMaps() # clear memoized color mappings
        k2b.apply(img, scale, method).show()
```

|Input|Method 0: 400.5 seconds|Method 1: 119.0 seconds|Method 2: 92.0 seconds|Method 3: 56.2 seconds|Method 4: 63.8 seconds|
|-|-|-|-|-|-|
|<img src="./input/ai/terribleautotranslation.png" width="300">|<img src="./readme/saver0.png">|<img src="./readme/saver1.png">|<img src="./readme/saver2.png">|<img src="./readme/saver3.png">|<img src="./readme/saver4.png">|
|(666×1184)|(300×533)|(300×533)|(300×533)|(300×533)|(300×533)|

|Input|Method 0: 1135.6 seconds|Method 1: 326.3 seconds|Method 2: 251.1 seconds|Method 3: 168.2 seconds|Method 4: 170.4 seconds|
|-|-|-|-|-|-|
|<img src="./input/ai/aiparty2019.png" width="300">|<img src="./readme/saver5.png">|<img src="./readme/saver6.png">|<img src="./readme/saver7.png">|<img src="./readme/saver8.png">|<img src="./readme/saver9.png">|
|(161×215)|(300×400)|(300×400)|(300×400)|(300×400)|(300×400)|

Another way to reduce the execution time of color map application is by scaling down the images used in initialization. Unlike gradient_transfer.py, scaling down the initialization images does not downgrade the color map too much and may even provide better results.

```python
high = Image.open('./input/ai/highrangetest.png')
love = Image.open('./input/ai/love.png')

cms = []
for scale in [1, 0.5, 0.1, 0.05, 0.01]:
    cm = ColorMap()
    cm.addMultiple([(kface, bface), (kbody, bbody)], scale)
    cms.append(cm)

for img in [high, love]:
    scale = 300 / min(img.size)
    for cm in cms:
        cm.initMaps() # clear memo
        cm.apply(img, scale, method=3).show()
```

|Color Map 0 (Input×1)|Color Map 1 (Input×0.5)|Color Map 2 (Input×0.1)|Color Map 3 (Input×0.05)|Color Map 4 (Input×0.01)|
|-|-|-|-|-|
|<img src="./readme/saver10.png" width="256">|<img src="./readme/saver11.png" width="256">|<img src="./readme/saver12.png" width="256">|<img src="./readme/saver13.png" width="256">|<img src="./readme/saver14.png" width="256">|
|8219 pixels|21624 pixels|3345 pixels|979 pixels|52 pixels|

|Input|Map 0: 60.1 seconds|Map 1: 147.3 seconds|Map 2: 26.0 seconds|Map 3: 8.7 seconds|Map 4: 1.2 seconds|
|-|-|-|-|-|-|
|<img src="./input/ai/highrangetest.png" width="300">|<img src="./readme/saver15.png">|<img src="./readme/saver16.png">|<img src="./readme/saver17.png">|<img src="./readme/saver18.png">|<img src="./readme/saver19.png">|
|(1650×1200)|(412×300)|(412×300)|(412×300)|(412×300)|(412×300)|

|Input|Map 0: 135.9 seconds|Map 1: 370.1 seconds|Map 2: 65.5 seconds|Map 3: 22.0 seconds|Map 4: 2.1 seconds|
|-|-|-|-|-|-|
|<img src="./input/ai/love.png" width="300">|<img src="./readme/saver20.png">|<img src="./readme/saver21.png">|<img src="./readme/saver22.png">|<img src="./readme/saver23.png">|<img src="./readme/saver24.png">|
|(400×600)|(300×450)|(300×450)|(300×450)|(300×450)|(300×450)|

(I assume the increase in initialized colors in Map 1 is due to the resampling filter.)

Now let's try all methods and all scales shown above applied to the artist profile picture to see how the script handles an image with a slightly different color palette.

```python
for method in range(5):
    for cm in cms:
        cm.initMaps() # clear memo
        cm.apply(artist, 0.27, method).show()
```

> All images below are of size (216×270).

|Method 0, Map 0|Method 0, Map 1|Method 0, Map 2|Method 0, Map 3|Method 0, Map 4|
|-|-|-|-|-|
|<img src="./readme/saver25.png">|<img src="./readme/saver26.png">|<img src="./readme/saver27.png">|<img src="./readme/saver28.png">|<img src="./readme/saver29.png">|
|572.7 seconds|1511.5 seconds|231.3 seconds|68.0 seconds|3.7 seconds|

|Method 1, Map 0|Method 1, Map 1|Method 1, Map 2|Method 1, Map 3|Method 1, Map 4|
|-|-|-|-|-|
|<img src="./readme/saver30.png">|<img src="./readme/saver31.png">|<img src="./readme/saver32.png">|<img src="./readme/saver33.png">|<img src="./readme/saver34.png">|
|162.0 seconds|412.2 seconds|65.1 seconds|16.4 seconds|1.2 seconds|

|Method 2, Map 0|Method 2, Map 1|Method 2, Map 2|Method 2, Map 3|Method 2, Map 4|
|-|-|-|-|-|
|<img src="./readme/saver35.png">|<img src="./readme/saver36.png">|<img src="./readme/saver37.png">|<img src="./readme/saver38.png">|<img src="./readme/saver39.png">|
|130.3 seconds|345.1 seconds|51.5 seconds|14.7 seconds|0.8 seconds|

|Method 3, Map 0|Method 3, Map 1|Method 3, Map 2|Method 3, Map 3|Method 3, Map 4|
|-|-|-|-|-|
|<img src="./readme/saver40.png">|<img src="./readme/saver41.png">|<img src="./readme/saver42.png">|<img src="./readme/saver43.png">|<img src="./readme/saver44.png">|
|75.9 seconds|204.8 seconds|41.5 seconds|14.0 seconds|1.4 seconds|

|Method 4, Map 0|Method 4, Map 1|Method 4, Map 2|Method 4, Map 3|Method 4, Map 4|
|-|-|-|-|-|
|<img src="./readme/saver45.png">|<img src="./readme/saver46.png">|<img src="./readme/saver47.png">|<img src="./readme/saver48.png">|<img src="./readme/saver49.png">|
|88.8 seconds|229.6 seconds|35.9 seconds|10.7 seconds|0.7 seconds|

## Other Scripts
- **gild_sprites.py** uses gradient_transfer.py to turn unpalettized Skullgirls Mobile portraits gold.
- **color_storage_test.py** tests efficiency of different structures for color storage for color_transfer.py.
