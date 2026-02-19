---
title: CRYPTOGRAFI
date: 2026-02-12 00:00:00
categories: [Pentest, DVWA]
tags: [cryptografi, cyber security, red team, dvwa]
---

## Intro

### Apa itu Cryptography?
Kriptografi adalah ilmu dan seni untuk menjaga kerahasiaan pesan dengan mengubahnya menjadi kode rahasia. Dalam dunia keamanan siber, kriptografi berperan penting untuk mengamankan data, memastikan keaslian pengguna (autentikasi), dan menjaga integritas informasi agar tidak dimanipulasi.

### Bagaimana Cara Kerjanya?
Secara sederhana, kriptografi bekerja dengan mengubah data yang bisa dibaca (plaintext) menjadi data acak yang tidak bisa dipahami (ciphertext) melalui proses yang disebut enkripsi. Proses ini membutuhkan sebuah kunci (key). Data yang telah dienkripsi hanya bisa dikembalikan ke bentuk aslinya melalui proses dekripsi dengan menggunakan kunci yang sesuai.

### Mengapa Bisa Rentan (Vulnerable)?
Meskipun tujuannya untuk mengamankan data, implementasi kriptografi sering kali memiliki kelemahan. Kerentanan muncul bukan hanya karena algoritmanya yang lemah, tetapi lebih sering karena kesalahan implementasi oleh pengembang. Beberapa contohnya adalah:

+ Menggunakan Encoding, Bukan Enkripsi: Seperti yang terlihat pada level Low di DVWA, pengembang salah mengartikan encoding (seperti XOR atau Base64) sebagai enkripsi.

+ Mode Enkripsi yang Lemah: Pada level Medium, aplikasi menggunakan mode ECB (Electronic Code Book) yang menyebabkan pola pada ciphertext masih bisa dikenali.

+ Kesalahan Konfigurasi: Penggunaan kunci yang statis atau Initialization Vector (IV) yang bisa ditebak.

### Apa Dampaknya Jika Berhasil Dieksploitasi?
Jika seorang attacker berhasil mengeksploitasi kelemahan kriptografi ini, dampaknya bisa sangat krusial:

+ Kebocoran Data Rahasia: Attacker bisa membaca data sensitif seperti password, token sesi, atau informasi pribadi pengguna lain.

+ Penyusupan Akun (Privilege Escalation): Pada level Medium, kita berhasil memanipulasi token untuk login sebagai Sweep dengan hak akses Admin. Ini membuktikan bahwa kelemahan kriptografi bisa digunakan untuk mengambil alih akun dan mendapatkan akses yang tidak seharusnya.

+ Modifikasi Data: Attacker bisa mengubah data yang terenkripsi tanpa mengetahui kuncinya, sehingga merusak integritas informasi.

## DVWA Cryptography 
Di DVWA ada modul tetang cryptography yang isinya adalah berbagai scenario pengguanaan cryptography yang rentan untuk dieksploit untuk setiap levelnya.

### **Level Low**

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image3.png)

Pada level Low, aplikasi menggunakan XOR encoding yang disalahpahami sebagai enkripsi. XOR (exclusive OR) adalah operasi bitwise sederhana yang bisa di-reverse dengan mudah jika kita mengetahui plaintext dan ciphertext-nya. Siapapun bisa mengembalikannya ke bentuk asli tanpa key.

Untuk yang pertama kita masukkan teks sembarang ke dalam kotak input, misalnya: "selamat pagi". untuk hasilnya adalah berupa teks "`BAQPCRkWGx8TAx4=`". 

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image4.png)

Selanjutnya kita coba untuk decode teks hasil encode tadi. dan hasilnya adalah teks kembali ke "selamat pagi".

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image5.png)

Disini kita coba pakai form decode dvwa untuk pesan yang hasil intercept. dan hasilnya adalah muncul teks "`Your new password is: Olifant`". kita berhasil meneukan passwornya, selanjutnya pas dicek juga berhasil juga

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image6.png)
![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image7.png)


Kita juga bisa cari tahu key untuk encode-nya. Pertama lihat outputnya, Jika outputnya berakhiran dengan tanda sama dengan (=) atau (==), itu ciri khas Base64. 

```
BAQPCRkWGx8TAx4=   <--- belakangnya ada tanda =
```

Sekarang kita coba untuk decode menggunakan tools online (cari "Base64 Decode"), hasilnya adalah teks yang tidak jelas seperti di bawah

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image8.png)

Jika Base64 tidak menghasilkan teks yang jelas atau aneh, kemungkinan itu adalah XOR Cipher. XOR adalah operasi logika bit. Kita coba dengan melakukan XOR antara plaintext `selamat pagi` dengan `hasil decode base64` tadi. Hasilnya Terlihat key-nya yaitu `wachtwoordw`

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image9.png)

Keunikannya dari operasi XOR adalah jika Ciphertext XOR Plaintext = Key.
Dan jika kita bandingkan dengan code di dvwa nya sama

> Pelajaran: Jangan gunakan encoding (Base64/Hex) atau XOR sederhana untuk mengamankan data rahasia. Itu bukan enkripsi!

### **Level Medium**

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image1.png)

Level Medium menggunakan AES-128-ECB (Electronic Code Book) yang merupakan mode enkripsi yang lemah. Kelemahan dari ECB adalah setiap blok plaintext dienkripsi satu satu dengan key yang sama, jadi kalau ada plaintext yang sama persis/serupa hasil chipertext nya juga sama.

Tujuan kita di level ini adalah untuk memanipulasi session token yang ada agar user Sweep bisa login dengan privilege Admin. Untuk bentuk session tokennya adalah seperti berikut :

```json
{
    "user": "example",
    "ex": 1723620372,
    "level": "user",
    "bio": "blah"
}
```

Kerentanan yang bisa dimanfaatkan adalah di penggunaan mode ECB, kita bisa langsung memotong dan menempel blok-blok enkripsi dari user yang berbeda untuk memalsukan identitas. Disini data yang kita punya 3 token hex panjang. karena ini aes-128, setipa blok berukuran 16 bytes = 32 karakter Hex. Mari kita potong-potong per 32 karakter.

**Sooty (admin, expired)**

```
e287af752ed3f9601befd45726785bd9 --> user : Sooty
b85bb230876912bf3c66e50758b222d0 --> ex : ....
837d1e6b16bfae07b776feb7afe57630 --> level : admin
5aec34b41499579d3fb6acc8dc92fd5f --> bio
cea8743c3b2904de83944d6b19733cdb --> bio
48dd16048ed89967c250ab7f00629dba --> bio
```

**Sweep (user, expired)**

```
3061837c4f9debaf19d4539bfa0074c1 --> user : sweep
b85bb230876912bf3c66e50758b222d0 --> ex : ....
83f2d277d9e5fb9a951e74bee57c77a3 --> level : user
caeb574f10f349ed839fbfd223903368 --> bio
873580b2e3e494ace1e9e8035f0e7e07 --> bio
```

**Soo (user, Valid)**

```
5fec0b1c993f46c8bad8a5c8d9bb9698 --> user : sweep
174d4b2659239bbc50646e14a70becef --> ex : ....
83f2d277d9e5fb9a951e74bee57c77a3 --> level : user
c9acb1f268c06c5e760a9d728e081fab --> bio
65e83b9f97e65cb7c7c4b8427bd44abc --> bio
16daa00fd8cd0105c97449185be77ef5 --> bio
```
selanjutnya adalah membuat token baru untuk Sweep agar bisa login sebagai admin. Kita perlu membuat token yang terdiri dari :

```
Nama: Sweep (Ambil Blok 1 dari token Sweep)
Waktu: Valid (Ambil Blok 2 dari token Soo)
Role: Admin (Ambil Blok 3 dari token Sooty)
Sisa: Padding (Ambil sisa blok dari token mana saja, misal Sweep)
```

dan pas disusun akan jadi seperti ini :

```
3061837c4f9debaf19d4539bfa0074c1 (Sweep)
174d4b2659239bbc50646e14a70becef (Expiry Valid milik Soo)
837d1e6b16bfae07b776feb7afe57630 (Role Admin milik Sooty)
caeb574f10f349ed839fbfd223903368 (Sisa data bio Sweep)
873580b2e3e494ace1e9e8035f0e7e07 (Sisa data bio Sweep)
```

Hasil Akhir (Gabungkan semua string di atas tanpa spasi):

```
3061837c4f9debaf19d4539bfa0074c1174d4b2659239bbc50646e14a70becef837d1e6b16bfae07b776feb7afe57630caeb574f10f349ed839fbfd223903368873580b2e3e494ace1e9e8035f0e7e07
```

Masukkan string panjang hasil gabungan tersebut ke kolom token dan submit.

![login_berhasil](/assets/image/2026-20-12-cryptography/image2.png)

Bisa dilihat login berhasil sebagai Sweep dengan hak akses Admin.

### Level High

Di sini aplikasi menggunakan AES-128-CBC (Cipher Block Chaining). Ini lebih baik dari ECB, tapi masih rentan.

>Blom nemu cara decrypt nya wkwkwkwkw

### Level Impossible

Pada level ini, Sudah menggunkan motede enkripsi yang modern dan paling sulit untuk ditembus

* AES-GCM (Galois/Counter Mode): 
    Tidak menggunakan padding (jadi tidak ada Padding Oracle Attack) dan memiliki fitur integrity check bawaan.

* Unique IV: 
    Setiap pesan dienkripsi dengan "bumbu" acak (IV/Nonce) yang berbeda, sehingga pesan yang sama akan memiliki ciphertext yang jauh berbeda.

* Key Management
    Kunci tidak di-hardcode di dalam file PHP yang bisa dibaca (idealnya disimpan di Environment Variable atau Hardware Security Module).
