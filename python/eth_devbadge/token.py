# standard imports
import os

# external imports
from chainlib.eth.tx import (
        TxFormat,
        TxFactory,
        )
from chainlib.eth.contract import (
        ABIContractEncoder,
        ABIContractType,
        )

# local imports
#from .interface import BadgeToken

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, 'data')


class BadgeToken(TxFactory):

    __abi = None
    __bytecode = None

    @staticmethod
    def abi():
        if BadgeToken.__abi == None:
            f = open(os.path.join(datadir, 'BadgeToken.json'), 'r')
            BadgeToken.__abi = json.load(f)
            f.close()
        return BadgeToken.__abi


    @staticmethod
    def bytecode():
        if BadgeToken.__bytecode == None:
            f = open(os.path.join(datadir, 'BadgeToken.bin'))
            BadgeToken.__bytecode = f.read()
            f.close()
        return BadgeToken.__bytecode


    @staticmethod
    def gas(code=None):
        return 1200000


    def constructor(self, sender_address, declarator, name, symbol, tx_format=TxFormat.JSONRPC):
        code = BadgeToken.bytecode()
        enc = ABIContractEncoder()
        enc.address(declarator)
        enc.string(name)
        enc.string(symbol)
        code += enc.get()
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.finalize(tx, tx_format)
