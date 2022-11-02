import json
import time

from eth_account import Account
import secrets, sys
from web3 import Web3
from api.aes_manager import encrypt, decrypt


def create_new_wallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    address = Account.from_key(private_key).address
    encrypted_private_key = encrypt(private_key).hex()
    return address, encrypted_private_key


def get_wallet_balance(contract_address, wallet_address):
    contract, web3, chain_id = get_contract(contract_address)
    resp = float(web3.fromWei(web3.eth.get_balance(wallet_address), 'ether'))
    return resp

def get_wallet_nft_balance(contract_address, wallet_address):
    contract, web3, chain_id = get_contract(contract_address)
    resp = contract.functions.balanceOf(wallet_address).call()
    return resp


def create_nft(contract_address, wallet, nft_id, admin_address, admin_pk):
    contract, web3, chain_id = get_contract(contract_address)

    mint_tx = contract.functions.mint(wallet)
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
    contract_data = load_data_from_file('./chains_data/contracts.json')[contract_address]
    chain_id = contract_data['chain']
    chain = load_data_from_file('./chains_data/chains.json')[contract_data['chain']]
    web3 = Web3(Web3.HTTPProvider(chain['node']))
    contract_abi = load_data_from_file('./chains_data/contracts_abi.json')[contract_data['abi']]
    contract = web3.eth.contract(address=web3.toChecksumAddress(contract_address), abi=contract_abi)
    return contract, web3, chain_id


def load_data_from_file(route):
    with open(route) as f:
        return json.load(f)


def get_chains_list():
    return load_data_from_file('chains_data/chains_list.json')


def get_wallet_nonce(contract_address, address):
    contract_data = load_data_from_file('./chains_data/contracts.json')[contract_address]
    chain = load_data_from_file('./chains_data/chains.json')[contract_data['chain']]
    web3 = Web3(Web3.HTTPProvider(chain['node']))
    return web3.eth.get_transaction_count(address)


def call_contract_function(contract_address, function_name, args, tx_args=None, nonce=None):
    
    contract, web3, chain_id = get_contract(contract_address)
    contract_function = getattr(contract.functions, function_name)

    if args is None:
        function = contract_function()
    elif type(args) is tuple or type(args) is list:
        function = contract_function(*args)
    else:
        function = contract_function(args)

    try:
        if tx_args is None:
            return {'error': '', 'message': function.call()}
        else:
            transaction_args = {}
            transaction_args['from'] = tx_args['sender_address']
            transaction_args['gasPrice'] = int(web3.eth.gasPrice)
            current_nonce = web3.eth.get_transaction_count(tx_args['sender_address'])
            if nonce is not None:
                if nonce < current_nonce:
                    return {'message': '', 'error': 'nonce cant be lower than ' + str(current_nonce)}
                transaction_args['nonce'] = nonce
            else:
                transaction_args['nonce'] = current_nonce
            if 'gas' in tx_args.keys():
                transaction_args['gas'] = tx_args['gas']
            tx = function.buildTransaction(transaction_args)
            sender_private_key = get_decrypted_text(tx_args['sender_private_key'])

            signed_txn = web3.eth.account.sign_transaction(tx, private_key=sender_private_key)
            
            resp = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            hex_resp = web3.toHex(resp)
            if len(hex_resp) == 66: return {'message': hex_resp, 'error': ''}
            return {'message': "", 'error': hex_resp}
    except Exception as e:
        print(e)
        print(e.args[0]['code'])
        return {'message': e.args[0]['message'], 'error': e.args[0]['code']}


def get_decrypted_text(encrypted_text):
    decrypted_data = decrypt(bytes.fromhex(encrypted_text))
    decrypted_text = decrypted_data.decode('utf8')
    return decrypted_text


def get_tx_status(contract_address, tx_id, type, deadline=600):
    _, web3, chain_id = get_contract(contract_address)
    tx_deadline = time.time() + deadline
    while time.time() < tx_deadline:
        try:
            tx_data = web3.eth.get_transaction_receipt(tx_id)
            if tx_data['status'] == 1:
                if type == 'nft':
                    token_id = web3.toInt(tx_data.logs[0].topics[3])
                    return {"error": "", "status": tx_data['status'],"from": tx_data['from'], "to": tx_data['to'], "token_id": token_id}
                else:
                    return {"error": "", "status": tx_data['status'],"from": tx_data['from'], "to": tx_data['to']}
            else:
                return {"error": "", "status": tx_data['status'], "from": tx_data['from'], "to": tx_data['to']}
        except Exception as e:
            pass
    return {"error": "Unable to get transaction status"}


def transfer(contract_address, amount, to, from_addres, from_pk, nonce=None):
    _, web3, chain_id = get_contract(contract_address)
    try:
        transaction_args = {}
        current_nonce = web3.eth.get_transaction_count(from_addres)
        if nonce is not None:
            if nonce < current_nonce:
                return {'message': '', 'error': 'nonce cant be lower than ' + str(current_nonce)}
            transaction_args['nonce'] = nonce
        else:
            transaction_args['nonce'] = current_nonce

        transaction_args['to'] = to
        transaction_args['value'] = web3.toWei(amount, 'ether')
        transaction_args['gas'] = 2000000
        transaction_args['gasPrice'] = int(web3.eth.gasPrice)
        transaction_args['chainId'] = int(chain_id)
        print(amount)
        print(from_addres)
        print(transaction_args)
        sender_private_key = get_decrypted_text(from_pk)
        # sign the transaction
        signed_tx = web3.eth.account.sign_transaction(transaction_args, sender_private_key)

        # send transaction
        resp = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        hex_resp = web3.toHex(resp)
        if len(hex_resp) == 66: return {'message': hex_resp, 'error': ''}
        return {'message': "", 'error': hex_resp}
    except Exception as e:
        return {'message': '', 'error': str(e)}
