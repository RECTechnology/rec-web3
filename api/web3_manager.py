import json
from eth_account import Account
import secrets
from web3 import Web3
from api.aes_manager import encrypt, decrypt


def create_new_wallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    address = Account.from_key(private_key).address
    config = load_data_from_file('../api/config/config.json')
    iv = config['iv']
    key = config['key']
    iv = bytes.fromhex(iv)
    key = bytes.fromhex(key)
    encrypted_private_key = encrypt(key, iv, private_key).hex()
    return address, encrypted_private_key


def get_wallet_nft_balance(contract_address, wallet_address):
    contract, web3 = get_contract(contract_address)
    resp = contract.functions.balanceOf(wallet_address).call()
    return resp


def create_nft(contract_address, wallet, nft_id, admin_address, admin_pk):
    contract, web3 = get_contract(contract_address)

    mint_tx = contract.functions.mint(wallet, nft_id)
    mint_tx = mint_tx.buildTransaction({
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


def call_contract_function(contract_address, function_name, args, tx_args=None):
    contract, web3 = get_contract(contract_address)
    contract_function = getattr(contract.functions, function_name)

    if args is None:
        function = contract_function()
    elif type(args) is tuple or type(args) is list:
        function = contract_function(*args)
    else:
        function = contract_function(args)

    if tx_args is None:
        return function.call()
    else:
        transaction_args ={}
        transaction_args['from'] = tx_args['sender_address']
        transaction_args['gasPrice'] = int(web3.eth.gasPrice)
        transaction_args['nonce'] = web3.eth.get_transaction_count(tx_args['sender_address'])
        if 'gas' in tx_args.keys():
            transaction_args['gas'] = tx_args['gas']
        tx = function.buildTransaction(transaction_args)
        sender_private_key = get_decrypted_text(tx_args['sender_private_key'])

        signed_txn = web3.eth.account.sign_transaction(tx, private_key=sender_private_key)
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        hex_tx = web3.toHex(tx_token)
        return hex_tx


def get_decrypted_text(encrypted_text):
    config = load_data_from_file('../api/config/config.json')
    iv = bytes.fromhex(config['iv'])
    key = bytes.fromhex(config['key'])
    decrypted_data = decrypt(key, iv, bytes.fromhex(encrypted_text))
    decrypted_text = decrypted_data.decode('utf8')
    return decrypted_text