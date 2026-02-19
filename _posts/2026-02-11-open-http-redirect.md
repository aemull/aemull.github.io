---
title: "DVWA : OPEN HTTP REDIRECT"
date: 2026-02-11 00.00.00
categories: [Pentest, DVWA]
tags: [http, cyber security, red team]
---

## **INTRO**

Open HTTP Redirect adalah kerentanan keamanan yang terjadi ketika sebuah aplikasi web menerima input dari pengguna dan menggunakannya untuk melakukan pengalihan (redirection) ke URL eksternal tanpa validasi yang cukup.

Biasanya, saat mengembangkan aplikasi menggunakan parameter seperti ?url=, ?next=, atau ?redirect= untuk mengarahkan pengguna kembali ke halaman tertentu setelah login atau aksi lainnya. Kerentanan muncul ketika kode PHP menggunakan fungsi header("Location: " . $input_user) secara langsung tanpa memeriksa apakah $input_user mengarah ke domain yang aman atau tidak.

Dampak Serangan :
+ Phishing: Penyerang dapat mengirimkan tautan yang terlihat resmi (dimulai dengan domain asli) namun mengarahkan korban ke situs palsu untuk mencuri kredensial.
+ Malware Distribution: Mengarahkan pengguna ke situs yang secara otomatis mengunduh file berbahaya.
+ Bypass Keamanan: Kadang digunakan untuk melewati proteksi CSRF atau OAuth jika whitelist domain tidak dikonfigurasi dengan benar.

## **Percobaan Serangan Open HTTP Redirect**

### Level Low

Dilihat dari kodennya, aplikasi mengambil nilai dari parameter redirect melalui metode GET dan langsung memasukkannya ke dalam fungsi header(). Tidak ada filter sama sekali.

```php
if (array_key_exists ("redirect", $_GET) && $_GET['redirect'] != "") {
    header ("location: " . $_GET['redirect']);
    exit;
}
```

Disini kita hanya perlu Ubah parameter pada URL agar mengarah ke situs eksternal, misalnya https://shopee.com.

Payload: 
```
http://localhost/vulnerabilities/open_redirect/source/low.php?redirect=https://shopee.com
```
![gambar_http_direct](assets/image/2026-02-11-open-http-redirect/image1.png)
![gambar_http_direct](assets/image/2026-02-11-open-http-redirect/image2.png)
![gambar_http_direct](assets/image/2026-02-11-open-http-redirect/image3.png)

### Level Medium

Pada level Medium, kode mencoba memblokir redirect ke URL absolut dengan menggunakan pola regex http:// atau https:// (case-insensitive).

```php
if (preg_match ("/http:\/\/|https:\/\//i", $_GET['redirect'])) {
    // Error: Absolute URLs not allowed.
} else {
    header ("location: " . $_GET['redirect']);
}
```

Namun, filter ini tidak sempurna karena masih mengizinkan:
* Protocol-relative URLs (misal //digi.ninja) — URL ini tidak mengandung http:// atau https://, sehingga lolos filter.
* Relative paths (misal ../../info.php) yang tetap berada dalam domain yang sama.

Kita coba dulu untuk akses halaman medium:

```
http://localhost/vulnerabilities/open_redirect/source/medium.php
```

![gambar_http_direct](assets/image/2026-02-11-open-http-redirect/image4.png)

Gunakan protocol-relative URL untuk mengarahkan ke situs eksternal:

```
http://localhost/vulnerabilities/open_redirect/source/medium.php?redirect=//digi.ninja
```
![gambar_http_direct](assets/image/2026-02-11-open-http-redirect/image5.png)

Browser akan menafsirkan //digi.ninja sebagai URL dengan protokol yang sama dengan halaman asal (misal http://), sehingga redirect tetap terjadi ke http://digi.ninja (atau https:// jika halaman asal menggunakan HTTPS).

![gambar_http_direct](assets/image/2026-02-11-open-http-redirect/image6.png)


### **Level High**

Pada level High, pengembang mencoba membatasi redirect hanya ke halaman info.php dengan memeriksa apakah string "info.php" ada di dalam parameter redirect. Pengecekan menggunakan strpos yang hanya mencari substring. Ini bisa dieksploitasi dengan menyisipkan info.php ke dalam URL eksternal, misalnya sebagai bagian dari query string atau path.

```php
<?php
if (array_key_exists ("redirect", $_GET) && $_GET['redirect'] != "") {
    if (strpos($_GET['redirect'], "info.php") !== false) {
        header ("location: " . $_GET['redirect']);
        exit;
    } else {
        http_response_code (500);
        ?>
        <p>You can only redirect to the info page.</p>
        <?php
        exit;
    }
}
http_response_code (500);
?>
<p>Missing redirect target.</p>
<?php
exit;
?>
```

Untuk eksplotasi kerentanan ini , kita bisa buat URL yang mengandung info.php di dalamnya, tetapi tetap mengarah ke situs eksternal. Contoh:

```
http://localhost/dvwa/vulnerabilities/open_redirect/source/high.php?redirect=https://digi.ninja/?a=info.php
```

Atau jika domain yang akan digunakan kebetulan memiliki path /info.php:

```
https://digi.ninja/info.php
```

![gambar_http_direct](assets/image/2026-02-11-open-http-redirect/image7.png)

Karena parameter mengandung substring "info.php", kondisi strpos terpenuhi, dan browser akan redirect ke https://digi.ninja/?a=info.php.

![gambar_http_direct](assets/image/2026-02-11-open-http-redirect/image7.png)

### **Level Impossible**

Pada level Impossible, aplikasi tidak lagi menerima URL langsung dari pengguna. Sebagai gantinya, parameter redirect harus berupa angka (is_numeric) dan hanya ada tiga nilai yang diperbolehkan (1, 2, 99). Masing-masing nilai sudah dipetakan ke target yang tetap (internal atau eksternal yang telah ditentukan). Dengan pendekatan whitelist ini, tidak ada celah bagi penyerang untuk memasukkan URL berbahaya.

```php
if (array_key_exists ("redirect", $_GET) && is_numeric($_GET['redirect'])) {
    switch (intval ($_GET['redirect'])) {
        case 1: $target = "info.php?id=1"; break;
        case 2: $target = "info.php?id=2"; break;
        case 99: $target = "https://digi.ninja"; break;
    }
    if ($target != "") {
        header ("location: " . $target);
    }
}
```

Kode bisa disebut aman dari Open Http redirect karena :
* Input dipastikan numerik, sehingga tidak bisa menyisipkan string URL.
* Tujuan redirect sudah ditentukan secara hardcoded, tidak bisa dimanipulasi.
* Tidak ada parameter lain yang dapat digunakan untuk mengubah target.

## **Kesimpulan**

Untuk mencegah Open Redirect, jangan pernah mempercayai input user untuk navigasi. Gunakan sistem ID mapping (seperti level Impossible) atau lakukan validasi ketat terhadap domain tujuan menggunakan whitelist yang hanya berisi domain internal perusahaan Anda.