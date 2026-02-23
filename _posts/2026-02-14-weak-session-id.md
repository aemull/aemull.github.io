---
title: " DVWA : Weak Session IDs"
date: 2026-02-17 00.00.00
categories: [Pentest]
tags: [Session, cyber security, red team]
---

## **INTRO**

### Apa Itu Session ID?
Session ID (SID) adalah sebuah string unik yang digunakan oleh aplikasi web untuk mengidentifikasi sesi pengguna. Ketika kita login ke suatu website, server akan membuat sesi baru dan memberikan kita sebuah Session ID, biasanya disimpan dalam cookie di browser kita. Setiap permintaan (request) selanjutnya akan menyertakan Session ID ini sehingga server tahu bahwa kita adalah pengguna yang sama.

### Bagaimana Cara Kerja Session ID?
1. Saat pengguna mengirim request login, server membuat sesi dan menghasilkan Session ID.
2. Server mengirimkan Session ID ke browser (biasanya melalui cookie).
3. Browser menyimpan cookie dan mengirimkannya kembali setiap kali mengakses halaman di domain yang sama.
4. Server mencocokkan Session ID dengan data sesi yang tersimpan di server (misalnya, siapa pengguna, hak akses, dll).
4. Dengan kata lain, Session ID adalah kunci untuk membuka pintu sesi kita.

### Kenapa Session ID Bisa Rentan?
Jika seorang penyerang berhasil mendapatkan Session ID korban, ia dapat membajak sesi (session hijacking) dan berpura-pura menjadi korban tanpa perlu tahu password. Kerentanan ini muncul jika:
+ Session ID mudah ditebak (predictable).
+ Session ID dikirim melalui koneksi tidak aman (HTTP).
+ Session ID tidak dirotasi setelah login atau logout.

Jadi menjaga keamanan session ID sama pentingnya dengan mengjaga keamanan password

## **PERCOBAAN SERANGAN DI DVWA**

![modul_dvwa](/assets/image/2026-02-14-weak-session-id/image2.png)

DVWA menyediakan modul Weak Session IDs untuk mempelajari bagaimana Session ID yang lemah dapat dieksploitasi. Modul ini terdiri dari empat tingkat kesulitan: Low, Medium, High, dan Impossible. Di setiap level, kita diminta untuk mencari tahu bagaimana nilai cookie dvwaSession dihasilkan, lalu menggunakannya untuk memprediksi ID sesi pengguna sistem lainnya.

> untuk session id dari modul ini (dvwaSession) tidak bisa dipakai untuk login, tapi konsep session id -nya masih sama dengan PHPSESSID untuk login dvwa
{: .prompt-warning }

### **Level Low**

Jika dilihat dari kodenya, Session ID hanya menggunakan counter yang bertambah 1 setiap kali ada permintaan. Ditambah lagui Session ID dikirim dalam bentuk plaintext. Hal tersebut menyebabkan session id sangat mudah ditebak


```php
<?php
$html = "";

if ($_SERVER['REQUEST_METHOD'] == "POST") {
    if (!isset ($_SESSION['last_session_id'])) {
        $_SESSION['last_session_id'] = 0;
    }
    $_SESSION['last_session_id']++; // <--- ini yang bikin session id mudah ditebak, cuma counter +1
    $cookie_value = $_SESSION['last_session_id'];
    setcookie("dvwaSession", $cookie_value); // <-- cookie berupa plaintext, gk ada enkripsi
}
?>
```

Untuk membuktikanya, kita langsung saja buka browser dan masuk ke Developer Tools dan buka tab Application atau Storage, setelah itu lihat bagian Cookie nya.

![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image1.png)

Saat pertama kali generate nilainya adalah 1, kita coba generate beberapakali untuk melihat pola dari session ID nya

![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image3.png)
![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image4.png)
![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image5.png)
![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image6.png)

Hasilnya adalah Session ID bertambah 1 setiap kali dilakukan generate:

```
Generate ke-1: dvwaSession = 1
Generate ke-2: dvwaSession = 2
Generate ke-3: dvwaSession = 3
Generate ke-4: dvwaSession = 4
Generate ke-5: dvwaSession = 5
```

Jika session ID kita saat ini adalah `10`, maka:
- User sebelum kita kemungkinan memiliki session ID: `9, 8, 7, 6...`
- User setelah kita kemungkinan memiliki session ID: `11, 12, 13, 14...`

Sebagai penyerang, kita dapat menebak bahwa sesi pengguna berikutnya akan bernilai n+1. Jika kita bisa mendapatkan ID sesi admin, kita tinggal mengatur cookie kita ke nilai tersebut.

### **Level Medium**

Di level medium, bisa dilihat dari code bahwa cookie diisi dengan nilai waktu UNIX (timestamp) saat generate. Timestamp adalah bilangan yang dapat diprediksi. Meskipun terlihat acak, sebenarnya ia bertambah setiap detik. Jika kita tahu kira-kira kapan pengguna lain generate session, kita bisa menebak nilainya.

```php
php
<?php
$html = "";
if ($_SERVER['REQUEST_METHOD'] == "POST") {
    $cookie_value = time();
    setcookie("dvwaSession", $cookie_value);
}
?>
```

Untuk melihat polanya, kita coba generate beberapa cookie untuk melihat nilainnya

![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image7.png)
![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image8.png)
![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image9.png)
![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image10.png)
![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image11.png)

```
Generate ke-1 : 1771261295 --> 2026-02-16 17:01:35 UTC
Generate ke-2 : 1771261303 --> 2026-02-16 17:01:43 UTC
Generate ke-3 : 1771261310 --> 2026-02-16 17:01:50 UTC
Generate ke-4 : 1771261320 --> 2026-02-16 17:02:00 UTC
Generate ke-5 : 1771261607 --> 2026-02-16 17:06:47 UTC

```

Bisa dilihat untuk nilai selalu bertambah seiring waktu. Jika kita tahu waktu generate sesi korban (misalnya berdasarkan aktivitas), kita bisa mencoba nilai di rentang waktu tersebut dengan dikombinasikan teknik Brute Force untuk menemukan Session ID yang valid.

Penggunaan Timestamp-based Session ID kelihatan lebih baik dari sequential counter, tapi masih gampang diprediksi kalau attacker punya informasi tentang waktu login.


### **Level Medium**

Di level high, jika dilihat dari source code terlihat bahwa cookie dihasilkan dengan:
+ Menggunakan counter (last_session_id_high) yang di-increment setiap generate.
+ Nilai counter kemudian di-hash dengan MD5.

```php
<?php
$html = "";
if ($_SERVER['REQUEST_METHOD'] == "POST") {
    if (!isset ($_SESSION['last_session_id_high'])) {
        $_SESSION['last_session_id_high'] = 0;
    }
    $_SESSION['last_session_id_high']++;
    $cookie_value = md5($_SESSION['last_session_id_high']);
    setcookie("dvwaSession", $cookie_value, time()+3600, "/vulnerabilities/weak_id/", $_SERVER['HTTP_HOST'], false, false);
}
?>
```

Format nilai dari Hash MD5 itu panjangnya 32 karakter heksadesimal. Meskipun hash terlihat acak, inputnya adalah angka berurutan. Artinya, kita bisa menghitung hash dari angka 1,2,3,... dan mencocokkan dengan cookie yang kita peroleh.

Untuk melihat polanya kita coba generate beberapa kali Session ID:

```
Generate 1: c4ca4238a0b923820dcc509a6f75849b (MD5 dari 1)
Generate 2: c81e728d9d4c2f636f067f89cc14862c (MD5 dari 2)
Generate 3: eccbc87e4b5ce2fe28308fd9f2a7baf3 (MD5 dari 3)
```

![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image12.png)
![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image13.png)
![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image14.png)

sekarang kita coba decrypt id session ini, bisa gunakan tools online atau langsung di terminal linux

```bash
echo -n "1" | md5sum
echo -n "2" | md5sum
echo -n "3" | md5sum
```
![Tampilan_awal_modul](/assets/image/2026-02-14-weak-session-id/image15.png)

Ternyata cocok! Jadi kita berhasil memetakan angka ke hash.

Untuk menebak sesi pengguna lain, kita hanya perlu tahu angka counter saat itu. Jika kita bisa mendapatkan satu hash, kita bisa mengetahui urutan counter dengan mendekripsinya. Setelah mengetahui pola, kita bisa membuat hash dari angka berikutnya dan mengatur cookie kita.

Hashing tanpa tambahan dan dengan input yang dapat ditebak tidak memberikan keamanan. Jadi Sebaiknya gunakan kombinasi data acak dan rahasia.

### Level Impossible

```php
<?php
$html = "";
if ($_SERVER['REQUEST_METHOD'] == "POST") {
    $cookie_value = sha1(mt_rand() . time() . "Impossible");
    setcookie("dvwaSession", $cookie_value, time()+3600, "/vulnerabilities/weak_id/", $_SERVER['HTTP_HOST'], true, true);
}
?>
```

Dilihat dari kodenya, level impossible menggunakan pendekatan yang jauh lebih aman:

1. Nilai cookie dibuat dengan sha1() dari gabungan:
    + mt_rand(): angka acak yang kuat.
    + time(): timestamp saat ini.
    + "Impossible": string statis sebagai tambahan.

2. Cookie dilengkapi parameter keamanan:
    + time()+3600: masa berlaku 1 jam.
    + path: dibatasi hanya untuk direktori /vulnerabilities/weak_id/.
    + domain: ditetapkan ke host server (mencegah cookie dikirim ke subdomain lain).
    + secure: true → cookie hanya dikirim melalui HTTPS.
    + httponly: true → cookie tidak dapat diakses oleh JavaScript (mengurangi risiko XSS).

Kenapa penerapan ini bisa dibilang aman?

+ Input yang digunakan sangat sulit ditebak: mt_rand() memberikan 2^32 kemungkinan, ditambah timestamp yang presisi, dan salt rahasia.
+ Hash SHA1 meskipun sudah usang, dengan input sebesar itu, menebak nilai cookie secara brute force tidak praktis.
+ Parameter keamanan mencegah serangan tambahan seperti session sniffing (dengan HTTPS) dan XSS (dengan HttpOnly).

