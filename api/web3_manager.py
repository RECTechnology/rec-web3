import json
from eth_account import Account
import secrets
from web3 import Web3


def create_new_wallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    address = Account.from_key(private_key).address
    return address, private_key


def get_wallet_nft_balance(contract_address, wallet_address):
    contract, web3 = get_contract(contract_address)
    resp = contract.functions.balanceOf(wallet_address).call()
    return resp


def create_nft(contract_address, wallet, nft_id, admin_address, admin_pk):
    contract, web3 = get_contract(contract_address)

    mint_tx = contract.functions.mint(wallet, nft_id).buildTransaction({
        'from': admin_address,
        'gasPrice': int(web3.eth.gasPrice),
        'nonce': web3.eth.get_transaction_count(admin_address),
    })
    signed_txn = web3.eth.account.sign_transaction(mint_tx, private_key=admin_pk)
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    hex_tx = web3.toHex(tx_token)
    return hex_tx


def get_contract(contract_address):
    contract_data = load_data_from_file('../chains_data/contracts.json')[contract_address]
    chain = load_data_from_file('../chains_data/chains.json')[contract_data['chain']]
    web3 = Web3(Web3.HTTPProvider(chain['node']))
    contract_abi = load_data_from_file('../chains_data/contracts_abi.json')[contract_data['abi']]
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    return contract, web3


def load_data_from_file(route):
    with open(route) as f:
        return json.load(f)


def get_chains_list():
    return load_data_from_file('chains_data/chains_list.json')
