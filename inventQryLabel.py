import qrcode
from PIL import Image, ImageDraw, ImageFont

class InventQryLabel(object):
    def __init__(self, label_size):
        self.w = w = label_size[0]
        self.h = h = label_size[1]

        self.qr_size = (h, h)
        self.text_size = (w - h, h)

        self.url = "http://atlas.hasi/"

    def mktext(self, string, font, fontsize):
        text = Image.new("1", self.text_size, color = 1)
        font = ImageFont.truetype(font, fontsize)
        draw = ImageDraw.Draw(text)
        # TODO perform text fitting and placing
        draw.text((0, 0), string, font=font)

        return text

    def gen_qrcode(self, id):
        # generate new qr code
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_Q, # 25% errors correctable
            box_size=10,
            border=2, # apparently the standard requires 4...
        )

        qr.add_data(self.url)
        qr.add_data(id)
        qr.make(fit=True)

        code = qr.make_image().resize(self.qr_size)

        return code

    def generate(self, id):
        # TODO get data for id

        # create binary (black/white) image
        im = Image.new("1", (self.w, self.h), color=1)

        code = self.gen_qrcode(id)
        # place code on upper-left corner
        im.paste(code, (0, 0))

        # create strings and place in the middle
        # TODO use data
        im.paste(self.mktext("Harry Plotter", "./harry.ttf", 50), (self.h, 0))
        im.paste(self.mktext("Besitzer: retep", "./Ubuntu-L.ttf", 30), (self.h, self.h//3))
        im.paste(self.mktext("ID: 1a2b", "./Ubuntu-L.ttf", 30), (self.h, self.h//3*2))

        # place logo on lower-right corner
        logo = Image.open("logo.png").convert("1").resize((self.h//2, self.h//2))
        im.paste(logo, (self.w - self.h//2 - 15//2, self.h//2))

        # output needs to be W < H, so rotate
        #final = im.rotate(90)
        final = im

        return final

    def print(self, image):
        image.save("out.png")

if __name__ == "__main__":
    inventQryLabel = InventQryLabel((514, 196))
    label = inventQryLabel.generate("1a2b")
    inventQryLabel.print(label)
