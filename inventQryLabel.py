#!/usr/bin/env python
import qrcode
from PIL import Image, ImageDraw, ImageFont
from subprocess import call

base_url = "http://hasi.it/i/"

class InventQryLabel(object):
    def __init__(self, label_size):
        self.w = w = label_size[0]
        self.h = h = label_size[1]

        self.qr_size = (h, h)
        self.text_size = (w - h, h)

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

        qr.add_data(base_url)
        qr.add_data(id)
        qr.make(fit=True)

        code = qr.make_image().resize(self.qr_size)

        return code

    def generate(self, name, owner, contact, usage_rule, uid):
        # create binary (black/white) image
        im = Image.new("1", (self.w, self.h), color=1)

        code = self.gen_qrcode(uid)

        # create font images
        name_txt = None
        if name == "Harry Plotter":
            name_txt = self.mktext(name, "./static/font/harry.ttf", 50)
        else:
            name_txt = self.mktext(name, "./static/font/Ubuntu-L.ttf", 43)
        owner_txt = self.mktext("Owner: {}".format(owner), "./static/font/Ubuntu-L.ttf", 30)
        contact_txt = self.mktext("Contact: {}".format(contact), "./static/font/Ubuntu-L.ttf", 30)
        permissions_txt = self.mktext("Permissions: {}".format(usage_rule), "./static/font/Ubuntu-L.ttf", 30)

        #logo = Image.open("./static/img/logo.png").convert("1").resize((self.h//2, self.h//2))

        # place image parts
        im.paste(code, (self.w-self.h, 0))
        im.paste(name_txt, (10, 5))
        im.paste(owner_txt, (10, self.h - 120))
        im.paste(contact_txt, (10, self.h - 80))
        im.paste(permissions_txt, (10, self.h - 40))
        #im.paste(logo, (self.w - self.h//2 - 15//2, self.h//2))

        # output needs to be W < H, so rotate
        final = im.rotate(90)

        return final

    def print(self, image):
        image.save("out.pbm")
        call([ "bash", "print" ])

if __name__ == "__main__":
    inventQryLabel = InventQryLabel((514, 196))
    label = inventQryLabel.generate("1a2b")
    inventQryLabel.print(label)
