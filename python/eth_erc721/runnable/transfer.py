"""Transfers an ERC721 NFT between accounts

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
import hashlib
from enum import Enum

# external imports
import chainlib.eth.cli
from chainlib.chain import ChainSpec
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.settings import ChainSettings
from chainlib.eth.settings import process_settings
from chainlib.eth.cli.arg import Arg
from chainlib.eth.cli.arg import ArgFlag
from chainlib.eth.cli.arg import process_args
from chainlib.eth.cli.log import process_log
from chainlib.eth.cli.config import Config
from chainlib.eth.cli.config import process_config
from chainlib.eth.constant import ZERO_CONTENT
from chainlib.eth.address import to_checksum_address
from hexathon import strip_0x

# local imports
from eth_erc721 import ERC721

logg = logging.getLogger()


def process_config_local(config, arg, args, flags):
    token_id_in = config.get('_POSARG')
    is_hex = False
    try:
        token_id = strip_0x(token_id_in)
        if token_id != token_id_in:
            is_hex = True
    except ValueError:
        pass

    token_id = None
    if is_hex:
        token_id = int(token_id_in, 16)
    else:
        token_id = int(token_id_in, 10)
    config.add(token_id, '_TOKEN_ID', False)

    return config


def process_settings_local(settings, config):
    settings.set('VALUE', config.get('_TOKEN_ID'))
    return settings


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_WRITE | arg_flags.WALLET | arg_flags.CREATE | arg_flags.VALUE | arg_flags.TAB | arg_flags.EXEC

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('token_id', type=str, nargs='*', help='Token ID to transfer. Prefix with 0x to specify as hex.')
args = argparser.parse_args(sys.argv[1:])

logg = process_log(args, logg)

config = Config()
config = process_config(config, arg, args, flags, positional_name='token_id')
config = process_config_local(config, arg, args, flags)
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
settings = process_settings_local(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))


def main():
    token_address = settings.get('EXEC')
    signer_address = settings.get('SENDER_ADDRESS')
    recipient = settings.get('RECIPIENT')
    value = settings.get('VALUE')
    conn = settings.get('CONN')
    g = ERC721(
            settings.get('CHAIN_SPEC'),
            signer=settings.get('SIGNER'),
            gas_oracle=settings.get('GAS_ORACLE'),
            nonce_oracle=settings.get('NONCE_ORACLE'),
            )
    
    (tx_hash_hex, o) = g.transfer_from(token_address, signer_address, signer_address, recipient, value, id_generator=settings.get('RPC_ID_GENERATOR'))

    if settings.get('RPC_SEND'):
        conn.do(o)
        if settings.get('WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                logg.critical('VM revert. Wish I could tell you more')
                sys.exit(1)
        print(tx_hash_hex)

    else:
        print(o['params'][0])


if __name__ == '__main__':
    main()

