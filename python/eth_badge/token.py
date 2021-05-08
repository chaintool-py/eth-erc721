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
        abi_decode_single,
        )
from chainlib.jsonrpc import jsonrpc_template
from chainlib.eth.constant import ZERO_ADDRESS
from hexathon import (
        add_0x,
        )

# local imports
from eth_erc721 import ERC721

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, 'data')


class BadgeToken(ERC721):

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
        return 2700000

    
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


    def mint_to(self, contract_address, sender_address, address, token_id, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('mintTo')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.UINT256)
        enc.address(address)
        enc.uint256(token_id)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx



    def minted_at(self, contract_address, token_id, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('mintedAt')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(token_id)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        return o


    @classmethod
    def parse_minted_at(self, v):
        return abi_decode_single(ABIContractType.UINT256, v)
