# standard imports
import logging
import unittest

# external imports
from eth_owned.unittest import TestInterface as TestInterfaceOwned

# local imports
from eth_badgetoken.unittest import TestBadgeToken
from eth_erc721.unittest.enum import TestInterface

logg = logging.getLogger()


class TestBasic(TestBadgeToken, TestInterface, TestInterfaceOwned):
    pass


if __name__ == '__main__':
    unittest.main()
