import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

ciphertext = base64.b64decode("PhQwGVA3q+T2mT+L3Pe5Vg==")
iv = base64.b64decode("MTIzNDU2NzgxMjM0NTY3OA==")

with open("wordlist.txt", "r") as f:
    for line in f:
        key = line.strip().encode()
        
        if len(key) not in [16,24,32]:
            continue
        
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ciphertext), AES.block_size)
            print("FOUND KEY:", key)
            print("PLAINTEXT:", pt)
            break
        except:
            pass