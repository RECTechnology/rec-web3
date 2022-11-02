import pyaes
from flask import current_app


def encrypt(_plaintext):
    # Encryption with AES-256-CBC
    iv = bytes.fromhex(current_app.config.get('IV'))
    key = bytes.fromhex(current_app.config.get('KEY'))
    encrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(key, iv))
    ciphertext = encrypter.feed(_plaintext.encode('utf8'))
    ciphertext += encrypter.feed()
    return ciphertext


def decrypt(_ciphertext):
    # Decryption with AES-256-CBC
    iv = bytes.fromhex(current_app.config.get('IV'))
    key = bytes.fromhex(current_app.config.get('KEY'))
    decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
    decryptedData = decrypter.feed(_ciphertext)
    decryptedData += decrypter.feed()
    return decryptedData


