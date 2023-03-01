# external imports
from hexathon import strip_0x
from chainlib.eth.nonce import RPCNonceOracle
# TODO: for mint, move to cic-contracts unittest
from eth_badgetoken import BadgeToken 
from chainlib.eth.tx import receipt

# local imports
from .base import TestInterface as TestInterfaceBase


class TestInterface(TestInterfaceBase):

    def test_token_index(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)

        token_bytes = b'\xee' * 32
        token_id_one = int.from_bytes(token_bytes, byteorder='big')
        (tx_hash_hex, o) = c.mint_to(self.address, self.accounts[0], self.accounts[1], token_id_one)
        r = self.rpc.do(o)

        token_bytes = b'\xee' * 32
        token_id_two = int.from_bytes(token_bytes, byteorder='big')
        (tx_hash_hex, o) = c.mint_to(self.address, self.accounts[0], self.accounts[2], token_id_two)
        r = self.rpc.do(o)

        o = c.token_by_index(self.address, 0, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        token = c.parse_token_by_index(r)
        self.assertEqual(token_id_one, token)

        o = c.token_by_index(self.address, 1, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        token = c.parse_token_by_index(r)
        self.assertEqual(token_id_two, token)



    def test_token_owner_index(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)

        token_bytes = b'\xee' * 32
        token_id_one = int.from_bytes(token_bytes, byteorder='big')
        (tx_hash_hex, o) = c.mint_to(self.address, self.accounts[0], self.accounts[1], token_id_one)
        r = self.rpc.do(o)

        token_bytes = b'\xee' * 32
        token_id_two = int.from_bytes(token_bytes, byteorder='big')
        (tx_hash_hex, o) = c.mint_to(self.address, self.accounts[0], self.accounts[2], token_id_two)
        r = self.rpc.do(o)

        o = c.token_of_owner_by_index(self.address, self.accounts[1], 0, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        token = c.parse_token_by_index(r)
        self.assertEqual(token_id_one, token)

        o = c.token_of_owner_by_index(self.address, self.accounts[2], 0, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        token = c.parse_token_by_index(r)
        self.assertEqual(token_id_two, token)
