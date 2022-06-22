from flask import Flask, jsonify, request
from api.web3_manager import create_new_wallet, create_nft, get_wallet_nft_balance

app = Flask(__name__)


@app.route('/test')
def test():
    return jsonify({'message': 'success'})


@app.route('/create_wallet', methods=['POST'])
def create_wallet():
    print(request.json)
    address, private_key = create_new_wallet()
    return jsonify({'message': 'success', 'wallet': {'address': address, 'private_key': private_key}})


@app.route('/create_nft', methods=['POST'])
def create_nft_():
    request_data = request.json
    print(request_data)
    contract_address = request_data['contract_address']
    wallet = request_data['wallet']
    nft_id = request_data['nft_id']
    admin_address = request_data['admin_address']
    admin_pk = request_data['admin_pk']
    transaction = create_nft(contract_address, wallet, nft_id, admin_address, admin_pk)
    return jsonify({'message': 'success', 'transaction': transaction})


if __name__ == '__main__':
    app.run(debug=True, port=4000)

