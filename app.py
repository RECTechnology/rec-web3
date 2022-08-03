from flask import Flask, jsonify, request
from api.web3_manager import create_new_wallet, create_nft, call_contract_function, get_wallet_nonce, get_tx_status, \
    get_wallet_balance, transfer
import logging

logging.basicConfig(filename = 'logs/app.log', level=logging.INFO, format = f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app = Flask(__name__)

@app.route('/test')
def test():
    app.logger.info("Getting test 2")
    return jsonify({'message': 'success'})

@app.route('/get_nonce')
def get_nonce():
    args = request.args
    if 'contract_address' not in args:
        return jsonify({'message': '', 'error': 'contract_address param is required'})
    if 'wallet' not in args:
        return jsonify({'message': '', 'error': 'wallet param is required'})
    print(args)
    app.logger.info("Getting nonce")
    contract_address = args['contract_address']
    wallet_address = args['wallet']
    nonce = get_wallet_nonce(contract_address, wallet_address)
    app.logger.info('nonce -> %s', nonce)
    return jsonify({'message': 'success', 'nonce': nonce})

@app.route('/get_transaction_status')
def get_transaction_status():
    args = request.args
    if 'contract_address' not in args:
        return jsonify({'message': '', 'error': 'contract_address param is required'})
    if 'transaction_id' not in args:
        return jsonify({'message': '', 'error': 'transaction_id param is required'})
    if 'transaction_type' not in args:
        type = 'transfer'
    else:
        type = args['transaction_type']

    print(args)
    app.logger.info('args -> %s', args)
    app.logger.info('type -> %s', type)
    contract_address = args['contract_address']
    transaction_id = args['transaction_id']
    status = get_tx_status(contract_address, transaction_id, type)
    app.logger.info('status -> %s', status)
    return jsonify(status)

@app.route('/get_balance')
def get_balance():
    args = request.args
    if 'contract_address' not in args:
        return jsonify({'message': '', 'error': 'contract_address param is required'})
    if 'wallet' not in args:
        return jsonify({'message': '', 'error': 'wallet param is required'})
    print(args)
    contract_address = args['contract_address']
    wallet_address = args['wallet']
    balance = get_wallet_balance(contract_address, wallet_address)
    return jsonify({'message': 'success', 'balance': balance})


@app.route('/create_wallet', methods=['POST'])
def create_wallet():
    address, private_key = create_new_wallet()
    return jsonify({'message': 'success', 'wallet': {'address': address, 'private_key': private_key}})


@app.route('/create_nft', methods=['POST'])
def create_nft_():
    request_data = request.json
    print(request_data)
    contract_address = request_data['contract_address']
    wallet_address = request_data['wallet']
    nft_id = request_data['nft_id']
    admin_address = request_data['admin_address']
    admin_pk = request_data['admin_pk']
    args = (wallet_address, nft_id)
    tx_args = {"sender_address": admin_address,
               "sender_private_key": admin_pk
               }
    transaction = call_contract_function(contract_address, 'mint', args, tx_args)
    return jsonify({'message': 'success', 'transaction': transaction})


@app.route('/contract_function_call', methods=['POST'])
def contract_function_call():
    request_data = request.json
    print(request_data)
    app.logger.info(request_data)
    if 'function_name' not in request_data:
        return jsonify({'message': '', 'error': 'function_name param is required'})
    function_name = request_data['function_name']
    if 'contract_address' not in request_data:
        return jsonify({'message': '', 'error': 'contract_address param is required'})
    contract_address = request_data['contract_address']

    args = request_data['args'] if 'args' in request_data.keys() else None
    tx_args = request_data['tx_args'] if 'tx_args' in request_data.keys() else None
    nonce = request_data['nonce'] if 'nonce' in request_data.keys() else None

    resp = call_contract_function(contract_address, function_name, args, tx_args, nonce)
    return jsonify(resp)

@app.route('/transfer', methods=['POST'])
def transfer_eth():
    request_data = request.json
    print(request_data)
    app.logger.info(request_data)
    if 'contract_address' not in request_data:
        return jsonify({'message': '', 'error': 'contract_address param is required'})
    contract_address = request_data['contract_address']

    if 'amount' not in request_data:
        return jsonify({'message': '', 'error': 'amount param is required'})
    amount = request_data['amount']

    if 'to' not in request_data:
        return jsonify({'message': '', 'error': 'to param is required'})
    to = request_data['to']

    if 'sender_address' not in request_data:
        return jsonify({'message': '', 'error': 'sender_address param is required'})
    sender_address = request_data['sender_address']

    if 'sender_private_key' not in request_data:
        return jsonify({'message': '', 'error': 'sender_private_key param is required'})
    sender_pk = request_data['sender_private_key']

    nonce = request_data['nonce'] if 'nonce' in request_data.keys() else None
    resp = transfer(contract_address, amount, to, sender_address, sender_pk, nonce)
    return jsonify(resp)


if __name__ == '__main__':
    app.run(debug=True, port=4000)
