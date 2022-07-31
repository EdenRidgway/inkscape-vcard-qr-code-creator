#!/usr/bin/env python
# coding=utf-8

import inkex
import re
import validators
import datetime
from render_barcode_qrcode import QrCode, QR8BitByte, QRCode, GridDrawer

# The word "QR Code" is registered trademark of
# DENSO WAVE INCORPORATED
#   http://www.denso-wave.com/qrcode/faqpatent-e.html

# vCard 4.0 Standard
# https://datatracker.ietf.org/doc/html/rfc6350


class VCardQRCode(QrCode):
    def __init__(self):
        super().__init__()

    def add_arguments(self, pars):
        super().add_arguments(pars)

        # Person
        pars.add_argument("--name", default="",
                          help="Full name (required)")
        pars.add_argument("--fname", default="",
                          help="First name, e.g. Mary")
        pars.add_argument("--mname", default="",
                          help="Middle name, e.g. Janice Jennifer")
        pars.add_argument("--surname", default="",
                          help="Last name, e.g. van de Namen")
        pars.add_argument("--nick", default="",
                          help="Nickname, e.g. Nicki the Great")
        pars.add_argument("--prefix", default="",
                          help="Name prefix, e.g. Capt., Prof.,...")
        pars.add_argument("--suffix", default="",
                          help="Name suffix, e.g. PhD, MD,...")
        pars.add_argument("--birthday", default="",
                          help="Date of birth, formatted like this: YYYYMMDD, e.g. 19700423")
        pars.add_argument("--photo", default="",
                          help="Photo URL, e.g. https://example.com/my_photo.jpg")

        # Personal contact info
        pars.add_argument("--phone_h", default="",
                          help="Phone number, e.g. +49 01234 123456")
        pars.add_argument("--email_h", default="",
                          help="Email address, e.g. me@example.com")
        pars.add_argument("--website_h", default="",
                          help="Website, e.g. https://example.com")
        pars.add_argument("--key_h", default="",
                          help="GPG public key URL, e.g. https://example.com/key.pgp")
        
        # Home address
        pars.add_argument("--pobox_h", default="",
                          help="Post office box, e.g. 12345 (note: leave blank if QR code doesn't work. Some readers cannot deal with this)")
        pars.add_argument("--add_extra_h", default="",
                          help="Address extra, e.g. Apartment 32B (note: leave blank if QR code doesn't work. Some readers cannot deal with this)")
        pars.add_argument("--street_h", default="",
                          help="Street and house number, e.g. Main Street 123")
        pars.add_argument("--city_h", default="",
                          help="City, e.g. Nairobi")
        pars.add_argument("--state_h", default="",
                          help="State/Province, e.g. CA")
        pars.add_argument("--postcode_h", default="",
                          help="Postal code, e.g. 12345")
        pars.add_argument("--country_h", default="",
                          help="Country, e.g. Kenia")

        # Work info
        pars.add_argument("--org", default="",
                          help="Organization, e.g. My Great Business")
        pars.add_argument("--title", default="",
                          help="Job title, functional position or function within the organization, e.g. Senior Interface Designer")
        pars.add_argument("--logo", default="",
                          help="Logo URL, e.g. https://example.com/logo.png")
        
        # Work contact info
        pars.add_argument("--phone_w", default="",
                          help="Phone number, e.g. +49 01234 123456")
        pars.add_argument("--email_w", default="",
                          help="E-mail address, e.g. contact@example.com")
        pars.add_argument("--website_w", default="",
                          help="Website, e.g. https://example.com")
        pars.add_argument("--key_w", default="",
                          help="GPG key URL, e.g. https://example.com/key.pgp")

        # Work address
        pars.add_argument("--pobox_w", default="",
                          help="Post office box, e.g. 12345 (note: leave blank if QR code doesn't work. Some readers cannot deal with this)")
        pars.add_argument("--add_extra_w", default="",
                          help="Address extra, e.g. House C (note: leave blank if QR code doesn't work. Some readers cannot deal with this)")
        pars.add_argument("--street_w", default="",
                          help="Street and house number, e.g. Main Street 123")
        pars.add_argument("--city_w", default="",
                          help="City, e.g. Nairobi")
        pars.add_argument("--state_w", default="",
                          help="State/Province, e.g. CA")
        pars.add_argument("--postcode_w", default="",
                          help="Postal code, e.g. 12345")
        pars.add_argument("--country_w", default="",
                          help="Country, e.g. Kenia")

        # Options
        pars.add_argument("--print", default=False, type=inkex.Boolean,
                          help="Display vCard as text message, so it can be copied.")

        # these can be ignored
        pars.add_argument("--nb", default="", 
                          help="Unused parameter, just ignore.") 
        pars.add_argument("--home_data", default="", 
                          help="Unused parameter, just ignore.")  
        pars.add_argument("--work_data", default="", 
                          help="Unused parameter, just ignore.")  

    def check_options(self):

        opts = ["name", "fname", "mname", "surname", "nick", "prefix", 
                   "suffix", "birthday", "photo", "phone_h", "email_h",
                   "website_h", "key_h", "pobox_h", "add_extra_h", "street_h", 
                   "city_h", "state_h", "postcode_h", "country_h", 
                   "org", "title", "logo", "phone_w", "email_w", 
                   "website_w", "key_w", "pobox_w", "add_extra_w", "street_w", 
                   "city_w", "state_w", "postcode_w", "country_w"]

        for opt in opts:
            self.clean_option(opt)
            val = vars(self.options)[opt]
            
            # email validation
            if opt.startswith('email'):
                if val and not validators.email(val):
                    inkex.errormsg(f"{val} is not a valid email address!")

            # url validation
            if opt in ["photo", "website_h", "key_h", "logo", "website_w", "key_w"]:
                if val and not validators.url(val, public=True):
                    inkex.errormsg(f"{val} is not a valid internet address!")
        
        # name must be given
        if vars(self.options)["name"] == "":
            inkex.errormsg("Please provide a full name!")
    
        # birthday validation
        val = vars(self.options)["birthday"]
        if val:
            try:
                datetime.datetime.strptime(val, '%Y%m%d')
            except ValueError:
                inkex.errormsg("Please format your birthday like this: 19700423!")


    def clean_option(self, opt):
        val = vars(self.options)[opt]
        val.strip()
        val.replace(",", "\,").replace(";", "\;")
        vars(self.options)[opt] = val

    def build_name(self):
        parts = ["surname", "fname", "mname", "prefix", "suffix"]
        fn = ";".join([vars(self.options)[part] for part in parts])
        return fn

    def build_address(self, type):
        if type == "home":
            opts = ["pobox_h", "add_extra_h", "street_h", "city_h", 
                    "state_h", "postcode_h", "country_h"]
        elif type == "work":
            opts = ["pobox_w", "add_extra_w", "street_w", "city_w", 
                    "state_w","postcode_w", "country_w"]
        res = ""

        values = [vars(self.options)[opt] for opt in opts]

        if any(values):    
            res = ";".join(values)
        return res

    def build_vCard(self, standardized_name, home_address, work_address): 
        
        format_strings = [
            ("name",      "FN:{}"),
            ("nick",      "NICKNAME:{}"),
            ("birthday",  "BDAY:{}"),
            ("photo",     "PHOTO:{}"),
            ("phone_h",   "TEL;TYPE=home:{}"),
            ("email_h",   "EMAIL;TYPE=home:{}"), 
            ("website_h", "URL;TYPE=home:{}"),
            ("key_h",     "KEY;TYPE=home;MEDIATYPE=application/pgp-keys:{}"),
            ("org",       "ORG:{}"),
            ("title",     "TITLE:{}"),
            ("logo",      "LOGO:{}"),
            ("phone_w",   "TEL;TYPE=work:{}"),
            ("email_w",   "EMAIL;TYPE=work:{}"),
            ("website_w", "URL;TYPE=work:{}"),
            ("key_w",     "KEY;TYPE=work;MEDIATYPE=application/pgp-keys:{}")
        ]
        
        vCardItems = ["BEGIN:VCARD","VERSION:4.0"]
        vCardItems.append(f"N:{standardized_name}")
        
        for fs in format_strings:
            val = vars(self.options)[fs[0]]
            if val:
                format_string = fs[1]
                vCardItems.append(format_string.format(val))
        
        if home_address:
            vCardItems.append(f"ADR;TYPE=home:{home_address}")
        if work_address:
            vCardItems.append(f"ADR;TYPE=work:{work_address}")

        vCardItems.append("END:VCARD")

        vCard = "\r\n".join(vCardItems)
        
        return vCard

    def generate(self):

        scale = self.svg.unittouu("1px")  # convert to document units
        opt = self.options

        if not opt.text:
            raise inkex.AbortExtension(_("Please enter an input text"))

        text_data = QR8BitByte(bytes(opt.text, "utf_8").decode("latin_1"))

        grp = inkex.Group()
        grp.set("inkscape:label", "vCard QR Code: " + self.options.name)

        pos_x, pos_y = self.svg.namedview.center
        grp.transform.add_translate(pos_x, pos_y)
        if scale:
            grp.transform.add_scale(scale)

        # GENERATE THE QRCODE

        # Automatic QR code size
        code = QRCode.getMinimumQRCode(text_data, opt.correctionlevel)

        self.boxsize = opt.modulesize
        self.invert_code = opt.invert
        self.margin = 4
        self.draw = GridDrawer(opt.invert, opt.smoothval)
        self.draw.set_grid(code.modules) 
        self.render_svg(grp, opt.drawtype)
        return grp

    def effect(self):
        
        self.check_options()

        standardized_name = self.build_name()
        home_address = self.build_address('home')
        work_address = self.build_address('work')

        vCard = self.build_vCard(standardized_name, home_address, work_address)

        # give result to QR code extension!
        self.options.text=vCard
        self.options.typenumber=0
        self.options.qrmode=0
        self.options.invert=False
        self.options.modulesize=self.options.modulesize
        self.options.drawtype="smooth"
        self.options.smoothness="neutral"
        self.options.pathtype="simple"
        self.options.smoothval=0.2
        self.options.symbolid=""
        self.options.groupid=""

        if self.options.print:
            inkex.utils.debug(vCard)

        super().effect()
            
if __name__ == '__main__':
    VCardQRCode().run()
