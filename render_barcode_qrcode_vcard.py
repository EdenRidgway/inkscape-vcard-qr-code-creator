#!/usr/bin/env python

import inkex
import re
import validators
import datetime

# The word "QR Code" is registered trademark of
# DENSO WAVE INCORPORATED
#   http://www.denso-wave.com/qrcode/faqpatent-e.html

# https://datatracker.ietf.org/doc/html/rfc6350

# The CHARSET parameter is no longer required as the vCard format now only supports one character set. Always UTF-8!
# Individual lines within vCard are delimited by the [RFC5322] line
#    break, which is a CRLF sequence (U+000D followed by U+000A).
# A line that begins with a white space character is a continuation of
#    the previous line, as described in Section 3.2.  The white space
#    character and immediately preceeding CRLF should be discarded when
#    reconstructing the original line.
# NEWLINE (U+000A) characters in values MUST be
#    encoded by two characters: a BACKSLASH followed by either an 'n'
#    (U+006E) or an 'N' (U+004E).
# FN
#    Purpose:  To specify the formatted text corresponding to the name of
#       the object the vCard represents.
#    Value type:  A single text value.
#    Cardinality:  1*
#    Special notes:  This property is based on the semantics of the X.520
#       Common Name attribute [CCITT.X520.1988].  The property MUST be
#       present in the vCard object.
#    Example:
#          FN:Mr. John Q. Public\, Esq.
# N
#    Purpose:  To specify the components of the name of the object the
#       vCard represents.
#    Value type:  A single structured text value.  Each component can have
#       multiple values.
#    Cardinality:  *1
#    Special note:  The structured property value corresponds, in
#       sequence, to the Family Names (also known as surnames), Given
#       Names, Additional Names, Honorific Prefixes, and Honorific
#       Suffixes.  The text components are separated by the SEMICOLON
#       character (U+003B).  Individual text components can include
#       multiple text values separated by the COMMA character (U+002C).
#       This property is based on the semantics of the X.520 individual
#       name attributes [CCITT.X520.1988].  The property SHOULD be present
#       in the vCard object when the name of the object the vCard
#       represents follows the X.520 model.
#    Examples:
#              N:Public;John;Quinlan;Mr.;Esq.
#              N:Stevenson;John;Philip,Paul;Dr.;Jr.,M.D.,A.C.P.

# ADR     the post office box;
#          the extended address (e.g., apartment or suite number);
#          the street address;
#          the locality (e.g., city);
#          the region (e.g., state or province);
#          the postal code;
#          the country name (full name in the language specified in
#          Section 5.1).

#       When a component value is missing, the associated component
#       separator MUST still be specified.
#       ADR;TYPE=work:;Suite D2-630;2875 Laurier;
#      Quebec;QC;G1V 2M2;Canada

# TYPE="home", TYPE="work"
# REV:19951031T222710Z
# VERSION:4.0 must come right after the start marker
# URL
# PHOTO;MEDIATYPE=image/jpeg:http://example.com/photo.jpg
# LOGO;MEDIATYPE=image/png:http://example.com/logo.png
# KEY;MEDIATYPE=application/pgp-keys:http://example.com/key.pgp

class VCardQRCode(inkex.Effect):
    def add_arguments(self, pars):

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
        pars.add_argument("--correctionlevel", default="", type=int,
                          help="Error correction level, values: 1 (Approx. 7%), 0 (Approx. 15%), 3 (Approx. 25%), 2 (Approx. 30%)")
        pars.add_argument("--modulesize", default="4", type=int,
                          help="Square size (px)")
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
                if val and not validators.is_email(val):
                    inkex.errormsg(f"{val} is not a valid email address!")

            # url validation
            if opt in ["photo", "website_h", "key_h", "logo", "website_w", "key_w"]:
                if val and not validators.is_url(val, public=True):
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


    def effect(self):
        
        self.check_options()

        standardized_name = self.build_name()
        home_address = self.build_address('home')
        work_address = self.build_address('work')

        vCard = self.build_vCard(standardized_name, home_address, work_address)

        # give result to QR code extension!

        if self.options.print:
            inkex.utils.debug(vCard)
            
if __name__ == '__main__':
    VCardQRCode().run()
