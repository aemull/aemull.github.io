import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# ==========================================
# 1. SISTEM SERVER (ORACLE)
# Server tahu kunci rahasia, attacker TIDAK tahu.
# ==========================================
SECRET_KEY = os.urandom(16)

def oracle_padding_check(iv, ciphertext):
    """
    Sistem akan mendekripsi data. 
    Mengembalikan True jika padding valid, False jika padding rusak.
    """
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    # Dekripsi ciphertext
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Cek PKCS#7 Padding secara manual
    last_byte = decrypted_data[-1]
    
    # Padding tidak boleh 0 atau lebih besar dari ukuran blok (16)
    if last_byte == 0 or last_byte > 16:
        return False
        
    # Validasi apakah sejumlah 'last_byte' di akhir bernilai sama
    for i in range(1, last_byte + 1):
        if decrypted_data[-i] != last_byte:
            return False
            
    return True # Padding Valid! (Server merespons normal)

# ==========================================
# 2. SETUP DATA AWAL (Kondisi saat Attacker menyadap)
# ==========================================
# Pesan asli "RAHASIA_DVWA_123" + 1 byte padding (0x01) agar pas 16 byte
plaintext_asli = b"RAHASIA_DVWA_123" + bytes([0x01]) 

# Enkripsi normal oleh sistem
iv_asli = os.urandom(16)
cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv_asli), backend=default_backend())
encryptor = cipher.encryptor()
ciphertext_asli = encryptor.update(plaintext_asli) + encryptor.finalize()

print("=== DATA YANG DISADAP ATTACKER ===")
print(f"IV Asli       : {iv_asli.hex()}")
print(f"Ciphertext    : {ciphertext_asli.hex()}\n")

# ==========================================
# 3. PROSES EKSPLOITASI OLEH ATTACKER
# Attacker hanya punya iv_asli, ciphertext_asli, dan akses ke fungsi oracle()
# Target: Mencari tahu byte terakhir dari plaintext (yang nilainya 0x01)
# ==========================================
print("=== MEMULAI PADDING ORACLE ATTACK (Mencari byte terakhir) ===")

byte_terakhir_iv = iv_asli[-1]
tebakan_ditemukan = None

# Attacker mencoba dari 0x00 sampai 0xFF (0 hingga 255)
for tebakan in range(256):
    # Kita ingin memanipulasi hasil dekripsi agar berakhiran 0x01 (padding valid untuk 1 byte)
    # Manipulasi IV: IV_baru = IV_asli XOR tebakan XOR 0x01
    iv_manipulasi = bytearray(iv_asli)
    iv_manipulasi[-1] = byte_terakhir_iv ^ tebakan ^ 0x01
    
    print(f"[*] Mencoba tebakan byte (Hex: {hex(tebakan)}) -> Kirim ke Oracle...", end=" ")
    
    # Lempar ke server (Oracle)
    if oracle_padding_check(bytes(iv_manipulasi), ciphertext_asli):
        print("RESPONS: BERHASIL (Padding Valid!)")
        tebakan_ditemukan = tebakan
        break # Hentikan pencarian karena tebakan benar
    else:
        print("RESPONS: Error")

# Hitung nilai asli setelah tebakan benar ditemukan
if tebakan_ditemukan is not None:
    print("\n=== HASIL EKSPLOITASI ===")
    print(f"[+] Nilai tebakan yang berhasil adalah: {hex(tebakan_ditemukan)}")
    print(f"[+] Berdasarkan matematika XOR, byte terakhir dari pesan asli adalah: {hex(tebakan_ditemukan)}")
    print(f"[+] Karakter ASCII-nya adalah: {chr(tebakan_ditemukan) if tebakan_ditemukan > 31 else 'Karakter Non-Printable (Padding)'}")