import time
from unittest import TestCase
from api.web3_manager import create_new_wallet, get_wallet_nft_balance, create_nft, call_contract_function,\
    get_wallet_nonce, get_tx_status
from api.aes_manager import encrypt, decrypt
import json


class TestConnection(TestCase):
    contract_address = "0xaf33ecfb3e5d07c232fc3ec8992e7de43485a70a"
    sharable_contract_address = "0x021FE99b04663B5Cf7ffbbC5fbC1eA87fdDE56ed"
    like_contract_address = "0x25f4c7adb709F47eb9b276F64409FC963d8c0CD0"
    endorse_contract_address = "0xC014900C972fC25499f141102a046c304D9670F1"

    def test_get_new_wallete(self):
        address, private_key = create_new_wallet()
        assert len(address) == 42
        assert len(private_key) == 160

    def test_get_nft_balance(self):
        wallet_address = "0xD329C1aACac84348887e06707C88f961917129AC"
        balance = get_wallet_nft_balance(self.contract_address, wallet_address)
        assert balance == 5

    def test_get_account_nonce(self):
        wallet_address = "0x8958913128df3EbC88E78f6e55Efe3bcD7C2BCFf"
        nonce = get_wallet_nonce(self.contract_address, wallet_address)
        assert nonce > 70

    def test_create_nft(self):
        nft_id = int(time.time())
        wallet_address = "0x8958913128df3EbC88E78f6e55Efe3bcD7C2BCFf"
        admin_wallet = self.load_data_from_file('./api/config/config.json')['admin_wallet']
        hex_tx = create_nft(self.contract_address, wallet_address, nft_id, admin_wallet['address'], admin_wallet['private_key'])
        # wait to validate tx before calling next tx
        time.sleep(10)
        assert len(hex_tx) == 66

    def load_data_from_file(self, route):
        with open(route) as f:
            return json.load(f)

    def test_call_get_nft_balance(self):
        wallet_address = "0xD329C1aACac84348887e06707C88f961917129AC"
        args = wallet_address
        resp = call_contract_function(self.contract_address, 'balanceOf', args)
        assert resp['error'] == ''
        assert resp['message'] == 5

    def test_call_create_nft(self):
        wallet_address = "0x0f145372eA0bBfbDc98837C14e966340b5C7B8ac"
        admin_wallet = self.load_data_from_file('./api/config/config.json')['admin_wallet']
        args = wallet_address
        config = self.load_data_from_file('./api/config/config.json')
        iv = bytes.fromhex(config['iv'])
        key = bytes.fromhex(config['key'])
        enctypted_data = encrypt(key, iv, admin_wallet['private_key'])
        encrypted_text = enctypted_data.hex()
        tx_args = {"sender_address": admin_wallet['address'],
                   "sender_private_key": encrypted_text
                   }
        resp = call_contract_function(self.sharable_contract_address, 'mint', args, tx_args)
        # wait to validate tx before calling next tx
        #time.sleep(10)
        assert resp['error'] == ''
        assert len(resp['message']) == 66

    def test_share_create_nft(self):
        wallet_address = "0x0f145372eA0bBfbDc98837C14e966340b5C7B8ac"
        admin_wallet = self.load_data_from_file('./api/config/config.json')['admin_wallet']
        args = [wallet_address, 0]
        config = self.load_data_from_file('./api/config/config.json')
        iv = bytes.fromhex(config['iv'])
        key = bytes.fromhex(config['key'])
        enctypted_data = encrypt(key, iv, admin_wallet['private_key'])
        encrypted_text = enctypted_data.hex()
        tx_args = {"sender_address": admin_wallet['address'],
                   "sender_private_key": encrypted_text
                   }
        resp = call_contract_function(self.sharable_contract_address, 'share', args, tx_args)
        # wait to validate tx before calling next tx
        #time.sleep(10)
        assert resp['error'] == ''
        assert len(resp['message']) == 66

    def test_call_get_contract_owner(self):
        admin_address = self.load_data_from_file('./api/config/config.json')['admin_wallet']['address']
        args = None
        resp = call_contract_function(self.contract_address, 'owner', args)
        assert resp['error'] == ''
        assert len(resp['message']) == 42
        assert resp['message'] == admin_address

    def test_encrypt_decrypt(self):
        plain_text = 'my plain text'
        config = self.load_data_from_file('./api/config/config.json')
        iv = bytes.fromhex(config['iv'])
        key = bytes.fromhex(config['key'])
        enctypted_data = encrypt(key, iv, plain_text)
        encrypted_text = enctypted_data.hex()
        decrypted_data = decrypt(key, iv, bytes.fromhex(encrypted_text))
        decrypted_text = decrypted_data.decode('utf8')
        assert decrypted_text == plain_text

    def test_get_tx_status_ok(self):
        tx_id = "0x7e4ad952a26a214f8235f607743998c130a35f351a7fec331447dadad4ba77e8"
        tx_data = get_tx_status(self.contract_address, tx_id)
        assert tx_data['status'] == 1
        assert tx_data['token_id'] == 33

    def test_get_tx_status_ko(self):
        tx_id = "0xf4b93a0dc25219c000807cadc28a7b96c5547716bd6bbd5ae146f9d0a3a58ebb"
        tx_data = get_tx_status(self.contract_address, tx_id)
        assert tx_data['status'] == 0