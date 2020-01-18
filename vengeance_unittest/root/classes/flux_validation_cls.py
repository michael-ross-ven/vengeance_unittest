
from string import ascii_lowercase
from random import choice

from unittest import TestCase
from vengeance import flux_cls


def flux_validation_cls(TestCase):
    def __init__(self):
        super().__init__()

        self.flux = instantiate_flux()
        self.assertRaises(NameError, self.validate_ac_request_field)

    def instantiate_flux(num_rows=100, num_cols=3, str_len=5):
        m = [['col_{}'.format(c) for c in ascii_lowercase[:num_cols]]]
        for _ in range(num_rows):
            m.append([''.join(choice(ascii_lowercase) for _ in range(str_len))
                                                      for _ in range(num_cols)])

        return flux_cls(m)



    def method_a(self):
        pass



