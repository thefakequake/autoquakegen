import math
from random import randint
from PIL import Image
from io import BytesIO
from base64 import b64encode

darken_map = {
    2: [3, 4, 5, 6],
    3: [2, 7],
    4: [2, 7],
    5: [2, 5, 7],
    6: [2, 6],
    7: [3, 4, 5, 7],
}


def darken(px, amount):
    r, g, b = px
    return max(0, r) - amount, max(0, g) - amount, max(0, b) - amount


def generate(filename):
    img = Image.new("RGB", (10, 10))
    from_colour = randint(0, 255), randint(0, 255), randint(0, 255)
    to_colour = randint(0, 255), randint(0, 255), randint(0, 255)

    width, height = img.size

    for x in range(width):
        for y in range(height):
            dist = (math.fabs(0 - x) + math.fabs(0 - y)) / (img.size[0] + img.size[1])
            r, g, b = map(
                lambda start, end: start + end,
                map(lambda start: start * (1 - dist), from_colour),
                map(lambda end: end * dist, to_colour),
            )
            px = int(r), int(g), int(b)
            img.putpixel((x, y), darken(px, 70) if x in darken_map.get(y, []) else px)

    buffer = BytesIO()
    resized = img.resize((1000, 1000), resample=Image.Resampling.BOX)
    resized.save(buffer, format="PNG")
    resized.save(filename, format="PNG")

    return f"data:image/png;base64,{b64encode(buffer.getvalue()).decode('utf-8')}"
