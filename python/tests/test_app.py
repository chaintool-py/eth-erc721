# standard imports
import os
import unittest
import json
import logging

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.connection import RPCConnection
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.address import to_checksum_address
from chainlib.eth.tx import (
        receipt,
        transaction,
        TxFormat,
        )
from chainlib.eth.contract import (
        abi_decode_single,
        ABIContractType,
        )
from chainlib.error import JSONRPCException
from hexathon import (
        add_0x,
        strip_0x,
        )


# local imports
from eth_devbadge.token import BadgeToken

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

testdir = os.path.dirname(__file__)


class Test(EthTesterCase):

    def setUp(self):
        super(Test, self).setUp()
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.constructor(self.accounts[0], b'\x00' * 20, 'DevBadge', 'DEV')
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        r = self.conn.do(o)
        logg.debug('deployed with hash {}'.format(r))
        
        o = receipt(r)
        r = self.conn.do(o)
        self.address = to_checksum_address(r['contract_address'])


    def _mint(self, recipient, token_id):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.mint_to(self.address, self.accounts[0], recipient, token_id)
        r = self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        return c


    def test_mint(self):
        token_bytes = b'\xee' * 32
        token_id = int.from_bytes(token_bytes, byteorder='big')
        c = self._mint(self.accounts[1], token_id)

        o = c.token_by_index(self.address, 0, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        self.assertEqual(token_bytes.hex(), strip_0x(r))

        o = c.total_supply(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        supply = c.parse_total_supply(r)

        self.assertEqual(supply, 1)


    def test_owner(self):
        token_bytes = b'\xee' * 32
        token_id = int.from_bytes(token_bytes, byteorder='big')
        c = self._mint(self.accounts[1], token_id)

        o = c.owner_of(self.address, token_id, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        owner_address = c.parse_owner_of(r)

        self.assertEqual(self.accounts[1], owner_address)

        o = c.token_of_owner_by_index(self.address, self.accounts[1], 0, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        self.assertEqual(token_bytes.hex(), strip_0x(r))


    def test_transfer(self):
        token_bytes = b'\xee' * 32
        token_id = int.from_bytes(token_bytes, byteorder='big')
        c = self._mint(self.accounts[1], token_id)

        nonce_oracle = RPCNonceOracle(self.accounts[1], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.transfer_from(self.address, self.accounts[1], self.accounts[1], self.accounts[2], token_id)
        r = self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = c.token_of_owner_by_index(self.address, self.accounts[1], 0, sender_address=self.accounts[0])
        with self.assertRaises(JSONRPCException):
            r = self.rpc.do(o)


        o = c.token_of_owner_by_index(self.address, self.accounts[2], 0, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        self.assertEqual(token_bytes.hex(), strip_0x(r))
       
if __name__ == '__main__':
    unittest.main()
