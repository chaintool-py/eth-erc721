"""Mints and gifts NFTs to a given address

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import sys
import os
import json
import argparse
import logging
import time

# external imports
import chainlib.eth.cli
from chainlib.eth.tx import receipt
from chainlib.chain import ChainSpec
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.address import to_checksum_address
from hexathon import (
        strip_0x,
        add_0x,
        )

# local imports
from eth_badgetoken import BadgeToken

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

arg_flags = chainlib.eth.cli.argflag_std_write | chainlib.eth.cli.Flag.EXEC | chainlib.eth.cli.Flag.WALLET
argparser = chainlib.eth.cli.ArgumentParser(arg_flags)
argparser.add_positional('token_id', type=str, help='32 bytes digest to use as token id')
args = argparser.parse_args()
extra_args = {
    'token_id': None,
    }
config = chainlib.eth.cli.Config.from_args(args, arg_flags, extra_args=extra_args, default_fee_limit=BadgeToken.gas())

wallet = chainlib.eth.cli.Wallet()
wallet.from_config(config)

rpc = chainlib.eth.cli.Rpc(wallet=wallet)
conn = rpc.connect_by_config(config)

chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))

token_id_bytes = bytes.fromhex(strip_0x(config.get('_TOKEN_ID')))
if len(token_id_bytes) != 32:
    token_id_int = None
    try:
        token_id_int = int(config.get('_TOKEN_ID'))
    except:
        token_id_int = strip_0x(config.get('_TOKEN_ID'))
        token_id_int = int(token_id_int, 16)
    token_id_bytes = token_id_int.to_bytes(32, byteorder='big')
    logg.info('numeric token id value {} parsed to {}'.format(config.get('_TOKEN_ID'), token_id_bytes.hex()))
token_id = int.from_bytes(token_id_bytes, byteorder='big')


def main():
    signer = rpc.get_signer()
    signer_address = rpc.get_sender_address()

    gas_oracle = rpc.get_gas_oracle()
    nonce_oracle = rpc.get_nonce_oracle()

    c = BadgeToken(chain_spec, signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle)

    recipient_address_input = config.get('_RECIPIENT')
    if recipient_address_input == None:
        recipient_address_input = signer_address

    recipient_address = add_0x(to_checksum_address(recipient_address_input))
    if not config.true('_UNSAFE') and recipient_address != add_0x(recipient_address_input):
        raise ValueError('invalid checksum address for recipient')

    token_address = add_0x(to_checksum_address(config.get('_EXEC_ADDRESS')))
    if not config.true('_UNSAFE') and token_address != add_0x(config.get('_EXEC_ADDRESS')):
        raise ValueError('invalid checksum address for contract')

    (tx_hash_hex, o) = c.mint_to(token_address, signer_address, recipient_address, token_id)
    if config.get('_RPC_SEND'):
        conn.do(o)
        if config.get('_WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert. Wish I had more to tell you')
                sys.exit(1)

        logg.info('mint to {} tx {}'.format(recipient_address, tx_hash_hex))
        print(tx_hash_hex)
    else:
        print(o)



if __name__ == '__main__':
    main()
