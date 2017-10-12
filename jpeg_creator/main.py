from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import argparse
import base64
from io import BytesIO

# This utility will generate a sequence of jpeg files for testing purposes.
# It an also base64 encode these jpegs and generate the JavaScript definitions for these images as a data URI:
# https://en.wikipedia.org/wiki/Data_URI_scheme
#
# Author: Colin Turner (koolspin)
# Dependencies: PIL

# Full path to the font to use when generating these jpegs
g_font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def validate_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("type", help="'data' will generate data URI js, 'file' will save jpegs to individual files", choices=['data', 'file'], default='file')
    parser.add_argument("count", help="How many jpegs to generate", type=int)
    args = parser.parse_args()
    if args.count is None:
        print("You must tell me how many files to generate", file=sys.stderr)
        return False, None, None
    else:
        return True, args.type, args.count


def create_image_file(fname, text, font_size):
    img = Image.new("RGB", (640, 480), "blue")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(g_font_path, font_size)
    draw.text((0, 0), text, (255, 255, 255), font=font)
    img.save(fname, optimize=True)


def create_image_base64(text, font_size):
    img = Image.new("RGB", (640, 480), "blue")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(g_font_path, font_size)
    draw.text((0, 0), text, (255, 255, 255), font=font)
    buf = BytesIO()
    img.save(buf, format="JPEG", optimize=True)
    return buf


def create_js_def(base64string, num):
    chars_per_line = 80
    str_index = 0
    str_len = len(base64string)
    print("// Image index {0}".format(num))
    print("imgarray.push('data:image/jpeg;base64,' +")
    while str_index < str_len:
        str_end = str_index + chars_per_line
        eol = " +"
        if str_end >= str_len:
            str_end = str_len
            eol = ");"
        foo = base64string[str_index:str_end]
        print("'{0}'{1}".format(foo, eol))
        str_index = str_end
    print("")


def save_images(count):
    for i in range(count):
        num = "{:02}".format(i)
        fname = "numbered_image_{0}.jpeg".format(num)
        create_image_file(fname, num, 216)


def base64_images(count):
    for i in range(count):
        num = "{:02}".format(i)
        buf = create_image_base64(num, 216)
        b64 = base64.b64encode(buf.getvalue())
        b64str = b64.decode()
        create_js_def(b64str, num)


res = validate_args()
if res[0]:
    if res[1] == 'data':
        base64_images(res[2])
    else:
        save_images(res[2])
    exit(0)
else:
    exit(1)

