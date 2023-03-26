from chainlib.eth.block import block_latest

# local imports
from eth_erc721.unittest.enum import TestInterface as TestInterfaceBase


class TestInterface(TestInterfaceBase):

    def test_minted_at(self):
        o = block_latest()
        r = self.rpc.do(o)
        block_start = int(r)
         
        self.backend.mine_blocks(42)

        token_bytes = b'\xee' * 32
        token_id = int.from_bytes(token_bytes, byteorder='big')
        c = self._mint(self.accounts[1], token_id)

        o = c.start_time(self.address, token_id, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        height = c.parse_start_time(r)
        self.assertEqual(height, block_start + 42 + 1)
