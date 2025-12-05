import hashlib
import base64
import json
import secrets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class DecryptorCore:
    # ⚠️ 密钥必须保持一致
    SEED = "yunmangongfang_2024_secret"
    SECRET_KEY = hashlib.sha256(SEED.encode()).digest()

    @classmethod
    def encrypt_data(cls, data: dict) -> str:
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            iv = secrets.token_bytes(16)
            cipher = AES.new(cls.SECRET_KEY, AES.MODE_CBC, iv)
            encrypted_bytes = cipher.encrypt(pad(json_str.encode('utf-8'), AES.block_size))
            combined = iv + encrypted_bytes
            return base64.urlsafe_b64encode(combined).decode('utf-8')
        except Exception as e:
            print(f"Encryption Error: {e}")
            return ""

    @classmethod
    def decrypt_data(cls, encrypted_str: str) -> dict:
        try:
            combined = base64.urlsafe_b64decode(encrypted_str)
            iv = combined[:16]
            ciphertext = combined[16:]
            cipher = AES.new(cls.SECRET_KEY, AES.MODE_CBC, iv)
            decrypted_json = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
            return json.loads(decrypted_json)
        except Exception as e:
            # print(f"Decryption Error: {e}")
            return None