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
from chainlib.eth.constant import ZERO_ADDRESS


# local imports
from eth_badgetoken import BadgeToken

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger(__name__)

testdir = os.path.dirname(__file__)


class TestBadgeToken(EthTesterCase):

    owner = None
    name = 'DevBadge'
    symbol = 'DEV'
    #decimals = 6
    initial_supply = 0

    def setUp(self):
        super(TestBadgeToken, self).setUp()
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = BadgeToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.constructor(self.accounts[0], 'DevBadge', 'DEV', self.accounts[1])
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        r = self.conn.do(o)
        logg.debug('deployed with hash {}'.format(r))
        
        o = receipt(r)
        r = self.conn.do(o)
        self.address = to_checksum_address(r['contract_address'])

        TestBadgeToken.owner = self.accounts[0]
