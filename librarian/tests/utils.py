from factory.fuzzy import FuzzyText

import re
import string

PROLLY_ROMAN_NUM = re.compile("^[%s]$" % (string.uppercase))
fuzzy_text = FuzzyText()

def make_name_object():
    return {"firstname": fuzzy_text.fuzz(), "lastname": fuzzy_text.fuzz()}
