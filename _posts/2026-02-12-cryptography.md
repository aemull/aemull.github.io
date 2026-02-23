---
title: "DVWA : CRYPTOGRAPHY"
date: 2026-02-12 00:00:00
categories: [Pentest, DVWA]
tags: [cryptography, cyber security, red team, dvwa]
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
Di DVWA ada modul tentang cryptography yang isinya adalah berbagai scenario penggunaan cryptography yang rentan untuk dieksploit untuk setiap levelnya.

### **Level Low**

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image3.png)

Pada level ini, aplikasi mengklaim dirinya sebagai sistem pesan yang aman. Di halaman utama, tersedia dua fitur utama: Encode dan Decode. Selain itu, halaman ini juga sudah menyediakan sebuah ciphertext yang perlu kita pecahkan:

```
Lg4WGlQZChhSFBYSEB8bBQtPGxdNQSwEHREOAQY=
```

"You have intercepted the following message, decode it and log in below."

Sistem ini menggunakan XOR encoding yang dilapisi Base64, lalu salah diklaim sebagai "enkripsi". Ini justru kerentanannya — encoding bukan enkripsi. Siapapun bisa membalikkannya tanpa membutuhkan kunci rahasia.

Untuk eksploitasinya, pertama kita coba pahami dulu cara kerjanya dengan memasukkan teks sembarang ke form Encode, misalnya selamat pagi. Hasilnya:

```
BAQPCRkWGx8TAx4=
```

Gambar: hasil encode teks "selamat pagi"

Perhatikan outputnya diakhiri tanda = — ini ciri khas Base64. Artinya data di-XOR dulu, baru hasilnya di-encode ke Base64.
Selanjutnya, kita coba decode kembali teks tadi menggunakan form Decode. Hasilnya kembali menjadi selamat pagi persis seperti semula.

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image4.png)

Ini membuktikan prosesnya sepenuhnya reversible tanpa kunci apapun.
Sekarang kita gunakan form Decode untuk memecahkan ciphertext yang disediakan halaman tadi:

```
Lg4WGlQZChhSFBYSEB8bBQtPGxdNQSwEHREOAQY=
```

Hasilnya muncul pesan: "Your new password is: Olifant"

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image6.png)

Kita masukkan password tersebut ke form login, dan berhasil masuk.

Gambar: login berhasil


Bonus: Mencari Tahu Kunci XOR-nya
Kita juga bisa membuktikan kelemahan ini lebih jauh dengan menemukan kunci yang digunakan, menggunakan sifat matematika XOR:
Ciphertext XOR Plaintext = Key
Caranya:

Decode Base64 dari output BAQPCRkWGx8TAx4= → hasilnya bytes acak yang tidak terbaca
XOR bytes tersebut dengan plaintext asli selamat pagi

Hasilnya terlihat key yang digunakan adalah wachtwoordw — dan jika dibandingkan langsung dengan source code DVWA, nilainya identik.

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image7.png)

>Pelajaran: Jangan gunakan encoding (Base64/Hex) atau XOR sederhana untuk mengamankan data rahasia. Encoding hanya menyamarkan data, bukan melindunginya. Siapapun yang tahu formatnya bisa langsung membalikkannya.


### **Level Medium**

![tampilan_gambar_medium](/assets/image/2026-20-12-cryptography/image1.png)

Level ini menggunakan AES-128-ECB (Electronic Code Book), algoritma enkripsi yang jauh lebih kuat dari XOR, tapi punya kelemahan di cara kerjanya.

ECB mengenkripsi setiap blok plaintext (16 byte) secara terpisah dan independen menggunakan kunci yang sama. Akibatnya, jika dua blok plaintext identik, ciphertext yang dihasilkan juga pasti identik. Ini memungkinkan kita untuk "memotong" dan "menempel" blok-blok ciphertext dari token yang berbeda untuk memanipulasi isi token tanpa perlu tahu kuncinya sama sekali.

Tujuan kita di level ini adalah login sebagai Sweep dengan hak akses Admin, dengan cara memanipulasi session token. Struktur token yang digunakan berbentuk JSON seperti ini:

```json
{
    "user": "example",
    "ex": 1723620372,
    "level": "user",
    "bio": "blah"
}
```

Halaman DVWA sudah menyediakan tiga token milik tiga user berbeda dalam format hex. Karena ini AES-128, setiap blok berukuran **16 byte = 32 karakter hex**. Kita potong token-token tersebut per 32 karakter untuk melihat isi tiap bloknya.

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

selanjutnya adalah tinggal membuat token baru untuk Sweep agar bisa login sebagai admin. Kita perlu membuat token yang terdiri dari :

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

Login berhasil sebagai Sweep dengan hak akses Admin, padahal kita tidak pernah tahu password-nya, apalagi kunci enkripsinya.


### **Level High**

![Level_high](/assets/image/2026-20-12-cryptography/image10.png)

Level ini menggunakan AES-128-CBC (Cipher Block Chaining) — mode enkripsi yang jauh lebih aman dari ECB. Tidak ada lagi kelemahan "blok identik = ciphertext identik". Tapi CBC punya titik lemah tersendiri: Padding Oracle Attack.

Berbeda dengan ECB, CBC mengaitkan setiap blok dengan blok sebelumnya melalui operasi XOR sebelum dienkripsi. Prosesnya seperti ini:
+ Enkripsi: 
    Plaintext di-XOR dengan ciphertext blok sebelumnya (atau IV untuk blok pertama), lalu hasilnya dienkripsi.
+ Dekripsi: 
    Ciphertext didekripsi, lalu di-XOR dengan ciphertext blok sebelumnya (atau IV) untuk menghasilkan plaintext.
+ Padding: 
    Karena AES bekerja per blok 16 byte, data yang kurang dari 16 byte akan ditambah padding menggunakan standar PKCS#7, byte padding bernilai sama dengan jumlah byte yang ditambahkan. Contoh: jika kurang 8 byte, maka ditambahkan 0x08 0x08 0x08 0x08 0x08 0x08 0x08 0x08.

Kerentanannya bukan di algoritma CBC-nya sendiri, tapi di respons server. Jika server memberikan respons berbeda antara "padding tidak valid" dan "padding valid tapi data salah", penyerang bisa mengeksploitasi perbedaan respons ini untuk mendekripsi data byte per byte tanpa perlu mengetahui kuncinya sama sekali. Inilah yang disebut Padding Oracle Attack.

Di DVWA level ini, server merespons dengan status 526 jika padding tidak valid, informasi kecil ini yang kita manfaatkan.

Sekarang tujuan kita adalah mengubah nilai token dari userid:2 menjadi userid:1 untuk mendapatkan akses sebagai admin.

Dari halaman DVWA, kita mendapatkan token dan IV dalam format Base64:

```json
{
  "token": "PhQwGVA3q+T2mT+L3Pe5Vg==",
  "iv": "MTIzNDU2NzgxMjM0NTY3OA=="
}
```

Selanjutnya kita download dulu script untuk mengeksploitasi kerentanan ini tersedia langsung di halaman DVWA, di bagian Hints. Download script oracle_attack.php dari sana.

Script ini bekerja dengan cara:
+ Memodifikasi IV byte demi byte dari kanan ke kiri
+ Mengirim IV yang sudah dimodifikasi ke server
+ Membaca respons server — apakah padding valid atau tidak
+ Dari pola respons tersebut, menghitung intermediate state (zeroing array)
+ XOR intermediate state dengan IV asli untuk mendapatkan plaintext

cara menjalankan scriptnya kita tinggal masukan token, iv, dan url request cek token.seperti ini contohnya

```bash
php oracle_attack.php --iv="MTIzNDU2NzgxMjM0NTY3OA==" --token="PhQwGVA3q+T2mT+L3Pe5Vg==" --url="http://localhost:4280/vulnerabilities/cryptography/source/check_token_high.php" > ./hasil_oracle.txt
```

Script akan bekerja offset per offset, dari byte paling kanan (offset 15) hingga paling kiri (offset 0):
```
Looking at offset 15 for padding 1 → Got hit for: 49
Looking at offset 14 for padding 2 → Got hit for: 61
Looking at offset 13 for padding 3 → Got hit for: 61
...
Looking at offset 0 for padding 16 → Got hit for: 84
```

![contoh_hasil](assets/image/2026-20-12-cryptography/image11.png)

Setelah semua 16 offset selesai diproses, script menghitung hasilnya:
```
Zeroing array  : 0x44 0x41 0x56 0x46 0x5c 0x52 0x0d 0x0a 0x39 0x3a 0x3b 0x3c 0x3d 0x3e 0x3f 0x30
Real IV        : 0x31 0x32 0x33 0x34 0x35 0x36 0x37 0x38 0x31 0x32 0x33 0x34 0x35 0x36 0x37 0x38
```

Plaintext berhasil terdekripsi:
```
Decrypted string with padding : 0x75 0x73 0x65 0x72 0x69 0x64 0x3a 0x32 0x08 0x08 0x08 0x08 0x08 0x08 0x08 0x08
Decrypted string without padding : 0x75 0x73 0x65 0x72 0x69 0x64 0x3a 0x32
Decrypted string as text : userid:2
```

Terlihat plaintext aslinya adalah `userid:2` dengan **8 byte padding** (`0x08` sebanyak 8 kali) — persis sesuai standar PKCS#7.

**Memanipulasi IV untuk Mengubah Plaintext**

Karena kita sudah tahu **zeroing array** (intermediate state dari dekripsi), kita bisa menghitung IV baru yang akan menghasilkan plaintext apapun yang kita inginkan, menggunakan rumus:
```
IV_baru = Zeroing Array XOR Plaintext_yang_diinginkan
```

Script secara otomatis menghitung ini. Target kita `userid:1`, dan IV baru yang dihasilkan:
```
New clear text : userid:1
New IV         : 0x31 0x32 0x33 0x34 0x35 0x36 0x37 0x3b 0x31 0x32 0x33 0x34 0x35 0x36 0x37 0x38
```

Perhatikan hanya satu byte yang berubah — dari 0x38 menjadi 0x3b di posisi offset 7. Perubahan kecil di IV, tapi efeknya langsung mengubah plaintext hasil dekripsi dari userid:2 menjadi userid:1.

Script kemudian mengirimkan token lama dengan IV baru ke server, dan responsnya:
```json
{
  "status": 200,
  "user": "Geoffery",
  "level": "admin"
}
```

Hack success! Token baru yang valid:

```json
{
  "token": "PhQwGVA3q+T2mT+L3Pe5Vg==",
  "iv": "MTIzNDU2NzsxMjM0NTY3OA=="
}
```

---

## KESIMPULAN

Cryptography adalah ilmu yang mengubah plaintext (data terbuka) menjadi ciphertext (data terenkripsi) menggunakan algoritma dan kunci, untuk menjaga kerahasiaan, autentikasi, dan integritas data.

Aplikasi menggunakan XOR encoding yang dilapisi Base64, bukan enkripsi sejati. Kelemahan ini membuat proses sepenuhnya reversible tanpa kunci rahasia — siapa pun bisa mendekompresi ciphertext langsung menjadi plaintext.

Mode ECB mengenkripsi setiap blok 16 byte secara independen. Jika dua blok plaintext identik, ciphertext juga identik. Attacker dapat memotong-tempel blok dari token berbeda untuk memanipulasi contents (nama user, role, waktu expiry) tanpa mengetahui kunci enkripsi.

Mode CBC lebih aman dari ECB, tapi punya kelemahan pada padding validation. Server memberi respons berbeda untuk padding invalid vs valid, sehingga attacker bisa melakukan Padding Oracle Attack untuk mendekripsi plaintext byte per byte dan mengkalkulasi IV baru untuk memanipulasi data sesuai keinginan.


