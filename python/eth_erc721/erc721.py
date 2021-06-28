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
from chainlib.jsonrpc import JSONRPCRequest
from chainlib.eth.constant import ZERO_ADDRESS
from hexathon import (
        add_0x,
        )
from eth_erc20 import ERC20
from eth_owned import EIP173


class ERC721(ERC20, EIP173):

    def transfer(self, contract_address, sender_address, recipient_address, value, tx_format=TxFormat.JSONRPC):
        raise NotImplementedError('EIP721 does not implement ERC20.transfer')


    def set_approve_for_all(self, contract_address, sender_address, operator_address, flag, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('setApprovalForAll')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.BOOLEAN)
        enc.address(operator_address)
        enc.uint256(int(flag))
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx

    
    def set_operator(self, contract_address, sender_address, operator_address, tx_format=TxFormat.JSONRPC):
        return self.set_approve_for_all(contract_address, sender_address, operator_address, True, tx_format=tx_format)


    def remove_operator(self, contract_address, sender_address, operator_address, tx_format=TxFormat.JSONRPC):
        return self.set_approve_for_all(contract_address, sender_address, operator_address, False, tx_format=tx_format)


    def token_by_index(self, contract_address, idx, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('tokenByIndex')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(idx)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    def owner_of(self, contract_address, token_id, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('ownerOf')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(token_id)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    def is_approved_for_all(self, contract_address, holder_address, operator_address, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('isApprovedForAll')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.ADDRESS)
        enc.address(holder_address)
        enc.address(operator_address)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    def is_operator(self, contract_address, token_id, operator_address, sender_address=ZERO_ADDRESS):
        return self.is_approved_for_all(contract_address, token_id, operator_address, sender_address=sender_address)


    def get_approved(self, contract_address, token_id, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('getApproved')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(token_id)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o



    def token_of_owner_by_index(self, contract_address, holder_address, idx, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('tokenOfOwnerByIndex')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.UINT256)
        enc.address(holder_address)
        enc.uint256(idx)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    def token_uri(self, contract_address, token_id, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('tokenURI')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(token_id)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    @classmethod
    def parse_owner_of(self, v):
        return abi_decode_single(ABIContractType.ADDRESS, v)


    @classmethod
    def parse_token_by_index(self, v):
        return abi_decode_single(ABIContractType.UINT256, v)


    @classmethod
    def parse_token_of_owner_by_index(self, v):
        return abi_decode_single(ABIContractType.UINT256, v)


    @classmethod
    def parse_total_supply(self, v):
        return abi_decode_single(ABIContractType.UINT256, v)


    @classmethod
    def parse_is_approved_for_all(self, v):
        return abi_decode_single(ABIContractType.BOOLEAN, v)


    @classmethod
    def parse_is_operator(self, v):
        return self.parse_is_approved_for_all(v)


    @classmethod
    def parse_get_approved(self, v):
        return abi_decode_single(ABIContractType.ADDRESS, v)


    @classmethod
    def parse_token_uri(self, v):
        return abi_decode_single(ABIContractType.STRING, v)
