import time
from unittest import TestCase
from api.web3_manager import create_new_wallet, get_wallet_nft_balance, create_nft
import json


class TestConnection(TestCase):

    def test_get_new_wallete(self):
        address, private_key = create_new_wallet()
        assert len(address) == 42
        assert len(private_key) == 66

    def test_get_nft_balance(self):
        contract_address = "0xaB81fFeB4aF5f90C6c85fe572f51DEEe5B12C792"
        wallet_address = "0xD329C1aACac84348887e06707C88f961917129AC"
        balance = get_wallet_nft_balance(contract_address, wallet_address)
        assert balance == 1

    def test_create_nft(self):
        nft_id = int(time.time())
        contract_address = "0xaB81fFeB4aF5f90C6c85fe572f51DEEe5B12C792"
        wallet_address = "0x8958913128df3EbC88E78f6e55Efe3bcD7C2BCFf"
        admin_wallet = self.load_data_from_file('../api/config/config.json')['admin_wallet']
        hex_tx = create_nft(contract_address, wallet_address, nft_id, admin_wallet['address'], admin_wallet['private_key'])
        assert len(hex_tx) == 66

    def load_data_from_file(self, route):
        with open(route) as f:
            return json.load(f)