# standard imports
import logging

# external imports
from hexathon import strip_0x
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.tx import receipt
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.block import block_latest
from chainlib.jsonrpc import JSONRPCException

# local imports
from eth_badgetoken import BadgeToken 

logg = logging.getLogger(__name__)


class TestInterface:

    def _mint(self, recipient, token_id):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.mint_to(self.address, self.accounts[0], recipient, token_id)
        r = self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)
        return c


    def test_token_owner(self):
        token_bytes = b'\xee' * 32
        token_id = int.from_bytes(token_bytes, byteorder='big')
        c = self._mint(self.accounts[1], token_id)

        o = c.owner_of(self.address, token_id, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        owner_address = c.parse_owner(r)
        self.assertEqual(strip_0x(self.accounts[1]), owner_address)

        o = c.token_of_owner_by_index(self.address, self.accounts[1], 0, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        self.assertEqual(token_bytes.hex(), strip_0x(r))


    def test_token_transfer_ownership(self):
        token_bytes = [
            b'\xee' * 32,
            b'\xdd' * 32,
            b'\xcc' * 32,
            ]
        token_ids = []
        for t in token_bytes:
            token_id = int.from_bytes(t, byteorder='big')
            token_ids.append(token_id)
            c = self._mint(self.accounts[0], token_id)

        o = c.total_supply(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        supply = c.parse_total_supply(r)
        self.assertEqual(supply, 3)

        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[0], self.accounts[4])
        r = self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        for t in token_ids:
            o = c.owner_of(self.address, token_id, sender_address=self.accounts[0])
            r = self.rpc.do(o)
            owner_address = c.parse_owner(r)
            self.assertEqual(strip_0x(self.accounts[4]), owner_address)

    def test_mint(self):
        o = block_latest()
        r = self.rpc.do(o)
        block_start = int(r)
         
        self.backend.mine_blocks(42)

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

        o = c.minted_at(self.address, token_id, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        height = c.parse_minted_at(r)

        self.assertEqual(height, block_start + 42 + 1)


    def test_approve(self):
        token_bytes = b'\xee' * 32
        token_id = int.from_bytes(token_bytes, byteorder='big')
        c = self._mint(self.accounts[1], token_id)

        nonce_oracle = RPCNonceOracle(self.accounts[1], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.approve(self.address, self.accounts[1], self.accounts[2], token_id)
        r = self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = c.get_approved(self.address, token_id, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        approved_address = c.parse_get_approved(r)
        self.assertEqual(approved_address, strip_0x(self.accounts[2]))

        nonce_oracle = RPCNonceOracle(self.accounts[2], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.transfer_from(self.address, self.accounts[2], self.accounts[1], self.accounts[3], token_id)
        r = self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = c.owner_of(self.address, token_id, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        owner_address = c.parse_owner_of(r)
        self.assertEqual(owner_address, strip_0x(self.accounts[3]))

        o = c.get_approved(self.address, token_id, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        approved_address = c.parse_get_approved(r)
        self.assertEqual(approved_address, strip_0x(ZERO_ADDRESS))


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
     

    def test_token_uri(self):
        token_bytes = b'\xee' * 32
        token_id = int.from_bytes(token_bytes, byteorder='big')
        c = self._mint(self.accounts[1], token_id)

        o = c.token_uri(self.address, token_id, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        uri = c.parse_token_uri(r)
        self.assertEqual(uri, 'sha256:' + token_bytes.hex()) 


    def test_operator(self):
        token_bytes = b'\xee' * 32
        token_id = int.from_bytes(token_bytes, byteorder='big')
        c = self._mint(self.accounts[1], token_id)

        nonce_oracle = RPCNonceOracle(self.accounts[1], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.set_operator(self.address, self.accounts[1], self.accounts[2])
        r = self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = c.is_operator(self.address, self.accounts[1], self.accounts[2], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        isop = c.parse_is_operator(r)
        self.assertTrue(isop)

        (tx_hash_hex, o) = c.remove_operator(self.address, self.accounts[1], self.accounts[2])
        r = self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = c.is_operator(self.address, self.accounts[1], self.accounts[2], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        isop = c.parse_is_operator(r)
        self.assertFalse(isop)

        (tx_hash_hex, o) = c.set_operator(self.address, self.accounts[1], self.accounts[2])
        r = self.rpc.do(o)

        nonce_oracle = RPCNonceOracle(self.accounts[2], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.transfer_from(self.address, self.accounts[2], self.accounts[1], self.accounts[3], token_id)
        r = self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = c.owner_of(self.address, token_id, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        owner_address = c.parse_owner(r)
        self.assertEqual(owner_address, strip_0x(self.accounts[3]))
