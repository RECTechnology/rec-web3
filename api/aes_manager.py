import pyaes


def encrypt(_key, _iv, _plaintext):
    # Encryption with AES-256-CBC
    encrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(_key, _iv))
    ciphertext = encrypter.feed(_plaintext.encode('utf8'))
    ciphertext += encrypter.feed()
    return ciphertext


def decrypt(_key, _iv, _ciphertext):
    # Decryption with AES-256-CBC
    decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(_key, _iv))
    decryptedData = decrypter.feed(_ciphertext)
    decryptedData += decrypter.feed()
    return decryptedData


