import time
from unittest import TestCase
from api.web3_manager import create_new_wallet, get_wallet_nft_balance, create_nft, call_contract_function
from api.aes_manager import encrypt, decrypt
import json


class TestConnection(TestCase):

    def test_get_new_wallete(self):
        address, private_key = create_new_wallet()
        assert len(address) == 42
        assert len(private_key) == 160

    def test_get_nft_balance(self):
        contract_address = "0xaf33ecfb3e5d07c232fc3ec8992e7de43485a70a"
        wallet_address = "0xD329C1aACac84348887e06707C88f961917129AC"
        balance = get_wallet_nft_balance(contract_address, wallet_address)
        assert balance == 2

    def test_create_nft(self):
        nft_id = int(time.time())
        contract_address = "0xaf33ecfb3e5d07c232fc3ec8992e7de43485a70a"
        wallet_address = "0x8958913128df3EbC88E78f6e55Efe3bcD7C2BCFf"
        admin_wallet = self.load_data_from_file('../api/config/config.json')['admin_wallet']
        hex_tx = create_nft(contract_address, wallet_address, nft_id, admin_wallet['address'], admin_wallet['private_key'])
        # wait to validate tx before calling next tx
        time.sleep(10)
        assert len(hex_tx) == 66

    def load_data_from_file(self, route):
        with open(route) as f:
            return json.load(f)

    def test_call_get_nft_balance(self):
        contract_address = "0xaf33ecfb3e5d07c232fc3ec8992e7de43485a70a"
        wallet_address = "0xD329C1aACac84348887e06707C88f961917129AC"
        args = wallet_address
        balance = call_contract_function(contract_address, 'balanceOf', args)
        assert balance == 2

    def test_call_create_nft(self):

        contract_address = "0xaf33ecfb3e5d07c232fc3ec8992e7de43485a70a"
        wallet_address = "0x0f145372eA0bBfbDc98837C14e966340b5C7B8ac"
        admin_wallet = self.load_data_from_file('../api/config/config.json')['admin_wallet']
        args = wallet_address
        config = self.load_data_from_file('../api/config/config.json')
        iv = bytes.fromhex(config['iv'])
        key = bytes.fromhex(config['key'])
        enctypted_data = encrypt(key, iv, admin_wallet['private_key'])
        encrypted_text = enctypted_data.hex()
        tx_args = {"sender_address": admin_wallet['address'],
                   "sender_private_key": encrypted_text
                   }
        hex_tx = call_contract_function(contract_address, 'mint', args, tx_args)
        # wait to validate tx before calling next tx
        time.sleep(10)
        assert len(hex_tx) == 66

    def test_call_get_contract_owner(self):
        contract_address = "0xaf33ecfb3e5d07c232fc3ec8992e7de43485a70a"
        admin_address = self.load_data_from_file('../api/config/config.json')['admin_wallet']['address']
        args = None
        owner_address = call_contract_function(contract_address, 'owner', args)
        assert len(owner_address) == 42
        assert owner_address == admin_address

    def test_encrypt_decrypt(self):
        plain_text = 'my plain text'
        config = self.load_data_from_file('../api/config/config.json')
        iv = bytes.fromhex(config['iv'])
        key = bytes.fromhex(config['key'])
        enctypted_data = encrypt(key, iv, plain_text)
        encrypted_text = enctypted_data.hex()
        decrypted_data = decrypt(key, iv, bytes.fromhex(encrypted_text))
        decrypted_text = decrypted_data.decode('utf8')
        assert decrypted_text == plain_text