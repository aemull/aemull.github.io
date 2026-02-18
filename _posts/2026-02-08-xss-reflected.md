---
title: XSS REFLECTED
date: 2026-02-05 00.00.00
categories: [Pentest]
tags: [xss, cyber security, red team]
---

# **Mengenai XSS Reflected**

***Cross-Site Scripting (XSS) Reflected*** adalah kerentanan keamanan dimana skrip berbahaya dimasukan melalui input pengguna dan langsung ditampilkan kembali pada halaman web tanpa proses validasi. Pada serangan ini, payload tidak disimpan secara permanen di server, melainkan dibawa melalui URL yang dimanipulasi (misalnya via link phishing). Dampak utama dari serangan ini adalah penyerang dapat mencuri session cookies, token autentikasi, atau melakukan action atas nama korban.

Karakteristik Reflected XSS:
* Payload ada di URL request
* Tidak persisten (tidak tersimpan di database)
* Memerlukan user untuk mengklik link berbahaya
* Dapat mencuri cookie, session token, atau informasi sensitif lainnya

Kerentanan terjadi karena:
* Input pengguna langsung dimasukkan ke output HTML tanpa sanitasi atau encoding
* Aplikasi mempercayai semua bentuk input dari pengguna
* Tidak ada filtering terhadap karakter khusus HTML/JavaScript


# **Percobaan Serangan XSS Reflected di DVWA**

Di DVWA ada modul khusus untuk XSS Reflected dengan tujuan utamanya adalah untuk mendapatkan Cookie user yang sedang login. Untuk 
tampilan halamannya hanya ada form inputan untuk nama saja

![tampilan-xss](/assets/image/2026-06-08-xss-reflected/image1.png)

dan bisa dilihat juga saat kita input dan submit kalimat dari form, maka akan muncul juga di url

![tampilan-xss](/assets/image/2026-06-08-xss-reflected/image2.png)

## **Level Low**

jika dilihat dari kodenya, tidak ada filter sama sekali dan setiap inputan langsung di-echo

```php
echo '<pre>Hello ' . $_GET[ 'name' ] . '</pre>';
```

sehingga saat kita memasukan payload yang berisi script javascript di url, makan akan ikut tereksekusi di clientnya. berikut contoh payload untuk mengambil cookie user

```
<script>alert(document.cookie);</script>
```

dan hasilnya akan menampilkan alert dengan isinya adalah cookie dari user
![tampilan-xss](/assets/image/2026-06-08-xss-reflected/image3.png)

## **Level Medium**

Untuk yang medium sendiri sudah menerapkan filter untuk tag javascript, tetapi hanya memfilter string `<script>` (lowercase). Jadi untuk `<Script>`, `<SCRIPT>`, `<ScRiPt>`, dll masih bisa digunakan karena tag di html itu tidak bersifat case-senstive.

```php
$name = str_replace( '<script>', '', $_GET[ 'name' ] );
```

Saat kita masukan payload misal dengan tag uppercase seperti `<SCRIPT>alert(document.cookie);</SCRIPT>`  , maka ini akan tetap tereksekusi di browser

![tampilan-xss](/assets/image/2026-06-08-xss-reflected/image4.png)

![tampilan-xss](/assets/image/2026-06-08-xss-reflected/image5.png)

dan terlihat hasilnya Cookie user bisa ditampilkan

## **Level High**

```php
$name = preg_replace( '/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i', '', $_GET[ 'name' ] );
```

Untuk yang high sudah menerapkan penghapusan tag `<script>` dengan regex yang kompleks, tetapi masih bisa kita bypass dengan menggunakan tag html lain atau event handler

contohnya untuk nanti payload nya bisa menggunakan tag untuk image

```html
<img src=x onerror=alert(document.cookie);>
```

![tampilan-xss](/assets/image/2026-06-08-xss-reflected/image6.png)

![tampilan-xss](/assets/image/2026-06-08-xss-reflected/image7.png)


## **Level Impossible**

untuk level ini sudah menerapkan beberapa pengamanan untuk mencegah xss, diantaranya adalah penggunaan function `htmlspecialchars()` untuk mengkonversi karakter khusus (encoding) HTML sehingga output tidak dieksekusi sebagai script

```php
$name = htmlspecialchars( $_GET[ 'name' ] );
```

disa sana juga menerapkan perlindungan untuk csrf token yang nantinya bisa mencegah serangan massal ke setiap user karena penyerang tidak bisa untuk mendapatkan CSRF token yang valid tanpa akses ke session user

```php
checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );
```

contoh serangannya adalah sebagai berikut

**Payload 1:**
```
?name=<script>alert('XSS')</script>&user_token=xxx
```
![token_invalid](/assets/image/2026-06-08-xss-reflected/image8.png)

**Hasil:** Token invalid, request ditolak


**Payload 2:**
```
?name=<img src=x onerror=alert('XSS')>&user_token=valid_token
```
![token_invalid](/assets/image/2026-06-08-xss-reflected/image10.png)
**Hasil:** Payload di-encode, muncul sebagai teks

