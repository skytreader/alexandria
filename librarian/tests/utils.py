import re
import string

PROLLY_ROMAN_NUM = re.compile("^[%s]$" % (string.uppercase))

def make_name_object(n):
    name = n.split()
    is_roman_num = PROLLY_ROMAN_NUM.match(name[-1])
    last_name = " ".join(name[-1:]) if is_roman_num else name[-1]
    first_name = name[0]

    return {"firstname": first_name, "lastname": last_name}
