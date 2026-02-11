---
title: XSS STORED
date: 2026-02-05 00.00.00
categories: [Pentest]
tags: [xss, cyber security, red team]
---

## Mengenai XSS Stored

Cross-Site Scripting (XSS) Stored adalah kerentanan keamanan di mana skrip berbahaya dimasukan melalui input pengguna dan disimpan secara permanen di database/server. Berbeda dengan Reflected XSS yang hanya sementara, Stored XSS akan menginfeksi semua pengguna yang mengakses halaman yang sudah terkontaminasi skrip berbahaya tadi.

Flow dari serangan :
![bagan_xss_stored](assets/2026-02-08-xss-stored/deepseek_mermaid_20260209_ba3ea3.png)

Karakteristik utama:
* Payload disimpan permanen di database.
* Tidak membutuhkan social engineering seperti reflected.
* Semua user yang membuka halaman akan terdampak.
* Dampak lebih berbahaya dibanding Reflected XSS.

Dampak:
* Pencurian cookie massal
* Merubah tampilan web (Defacement) permanen
* Redirect semua user ke situs bahaya
* Keylogging massal

## Percobaan Serangan XSS Stored di DVWA

pada DVWA disediakan modul yang rentan terhadap xss stored. untuk tampilannya dalah berupa form untuk input nama dan pesan teks

![bagan_xss_stored](assets/2026-02-08-xss-stored/image1.png)

disini tujuan utama kita adalah untuk redirect user ke halaman web yang kita tentukan, disini saya akan melakukan redirecting ke halaman web ecomerce shopee

![bagan_xss_stored](assets/2026-02-08-xss-stored/image2.png)


### Level Low

Jika melihat kodenya, hanya ada `mysqli_real_escape_string()` untuk perlindungan dari SQL injection. Tidak ada HTML encoding juga disana jadi inputan langsung disimpan di database dan ditampilkan lansung ke user.

```php
// Message: hanya stripslashes() dan mysqli_real_escape_string()
$message = stripslashes( $message );
$message = mysqli_real_escape_string($message);

// Name: hanya mysqli_real_escape_string()
$name = mysqli_real_escape_string($name);

// Query: langsung concatenate
$query = "INSERT INTO guestbook VALUES ( '$message', '$name' );";
```
contoh serangannya adalah saat penyerang menyisipkan file javascript kedalam kolom name seperti berikut

```html
<script>window.location='https://shopee.co.id/search?keyword=mini%20pc'</script>
```

maka setiap user yang melihat massage tersebut akan diredirect ke halaman lain. Tapi sebelum dimasukan, terlebih dahulu kita harus menambah jumlah ukuran dari form input name karena defaultnya hanya diset di 10 karakter saja.

![bagan_xss_stored](assets/2026-02-08-xss-stored/image3.png)

jadi nanti script diatas bisa dimasukan 

![bagan_xss_stored](assets/2026-02-08-xss-stored/image4.png)

dan saat ada user membuka page tersebut, maka akan otomatis diredirect

### Level Medium

untuk level maedium baru sebagian yang sudah diberikan perlindungan dengan menambhakan encoding dan dan menghapus semua tag HTML atau PHP yang ada. tapi ini hanya berlaku untuk form Massage, untuk yang name itu masih rentan karena untuk filter inputannya masih menggunakan filter manual yang case-sensitive

```php
// Message: strip_tags() + htmlspecialchars() → AMAN
$message = strip_tags( addslashes( $message ) );
$message = mysqli_real_escape_string($message);
$message = htmlspecialchars( $message );

// Name: hanya str_replace('<script>', '', $name) → RENTAN
$name = str_replace( '<script>', '', $name );
$name = mysqli_real_escape_string($name);
```

untuk percobaanya masih sama seperti diatas, kita mengubah dulu ukuran jumlah karakter di form name, dan masukan script dibawah di form name.

```html
<SCRIPT>alert(document.cookie);</SCRIPT>
```

![bagan_xss_stored](assets/2026-02-08-xss-stored/image5.png)

dan kalu kita input ke form massage, maka kode tidak akan tereksekusi karena sudah terfilter sebelumnya

![bagan_xss_stored](assets/2026-02-08-xss-stored/image6.png)


### Level High

Untuk level high ini ditambahkan regex untuk menargetkan kata "script" pada form username, akan tetapi masih belum bisa menangani HTML event, SVG, iframe, dan javascript URI.

```php
// Message: strip_tags() + htmlspecialchars() → AMAN
$message = strip_tags( addslashes( $message ) );
$message = mysqli_real_escape_string($message);
$message = htmlspecialchars( $message );

// Name: preg_replace() untuk <script> tag → MASIH RENTAN
$name = preg_replace( '/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i', '', $name );
$name = mysqli_real_escape_string($name);
```

contoh yang bisa diinputkan adalah seperti berikut

```html
<img src=x onerror="window.location='https://shopee.co.id/search?keyword=mini%20pc'">
```

untuk pecobaanya masih sama dengan mengubah ukuran banyak karakter yang bisa diinputkan menggunakan developer tool. selanjutnya inputkan script diatas ke dalam form name, dan script akan disimpan diserver

![bagan_xss_stored](assets/2026-02-08-xss-stored/image8.png)

jika diisi di form massage, maka scriptnya akan hilang

![bagan_xss_stored](assets/2026-02-08-xss-stored/image7.png)

![bagan_xss_stored](assets/2026-02-08-xss-stored/image9.png)

### Level Impossible

untuk level ini sudah menerapakan banyak filter dan pengamanan didalamnya

```php
// 1. Anti-CSRF token
checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );

// 2. htmlspecialchars() untuk kedua field
$message = htmlspecialchars( $message );
$name = htmlspecialchars( $name );

// 3. Prepared statements untuk SQL
$data = $db->prepare( 'INSERT INTO guestbook VALUES ( :message, :name );' );
$data->bindParam( ':message', $message, PDO::PARAM_STR );
$data->bindParam( ':name', $name, PDO::PARAM_STR );
$data->execute();
```

1. htmlspecialchars() pada Semua Output

di level ini sudah menerapkan encoding yang akan merubah karakter karakter khusus dari html. Misalkan kita melakukan input pada form berupa `<img src=x onerror="alert(1)">`, maka ouputnya adalah `&lt;img src=x onerror=&quot;alert(1)&quot;&gt;` dan dirender sebagai teks bukan html. Dan ini berlaku untuk kedua form

```php
$message = htmlspecialchars( $message );
$name = htmlspecialchars( $name );
```

![bagan_xss_stored](assets/2026-02-08-xss-stored/image10.png)

![bagan_xss_stored](assets/2026-02-08-xss-stored/image11.png)


2. Prepared Statements dan Anti-CSRF Token

di level ini juga menambahka prepared statements untuk mencegah sql injection dan Anti CSRF token untuk mencegah serangan CSRF pada user

```php
$data = $db->prepare( 'INSERT INTO guestbook VALUES ( :message, :name );' );
$data->bindParam( ':message', $message, PDO::PARAM_STR );
``` 

```php
checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );
```

jadi untuk Level Impossible ini sudah memenuhi keperluan untuk pengamanan dari XSS