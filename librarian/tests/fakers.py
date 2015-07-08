from faker import Faker
from faker.providers import BaseProvider

import random
import string

fake = Faker()

class BookFieldsProvider(BaseProvider):
    ADJECTIVES = ("beautiful", "wonderful", "abstruse", "astute", "bad", "good",
      "austere", "sinister", "jolly", "helpful", "ersatz", "slippery", "penultimate",
      "unyielding", "intimidating", "wistful", "vile", "carmivorous", "miserable")
    NOUNS = ("computer", "formula", "equation", "waters", "rain", "fight",
      "hope", "dream", "love", "library", "book", "elevator", "hospital",
      "village", "academy", "goblet", "chamber", "carnival", "hero")

    def isbn(self, thirteen = True):
        if thirteen:
            isbn = "".join([random.choice(string.digits) for _ in range(12)])

            # calculate the check-digit
            check_digit = 0
            one_toggle = True
            
            for digit in isbn:
                d = int(digit)
                if one_toggle:
                    check_digit += d
                else:
                    check_digit += d * 3

                one_toggle = not one_toggle
            
            check_digit = (10 - (check_digit % 10)) % 10
            
            return isbn + str(check_digit)
        else:
            isbn = "".join([random.choice(string.digits) for _ in range(9)])

            # calculate the check-digit
            check_digit = 0
            multiplier = 10

            for digit in isbn:
                check_digit += int(digit) * multiplier
                multiplier -= 1

            check_digit = ((11 - check_digit) % 11) % 11
            
            if check_digit == 10:
                return isbn + "X"
            
            return isbn + str(check_digit)

    def title(self):
        return " ".join(("The",
          random.choice(BookFieldsProvider.ADJECTIVES).capitalize(),
          random.choice(BookFieldsProvider.NOUNS).capitalize()))
