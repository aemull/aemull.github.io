---
title: "DVWA : CSP BYPASS"
date: 2026-02-11 00.00.00
categories: [Pentest, DVWA]
tags: [CSP, cyber security, red team]
---

## **INTRO**

**Content Security Policy (CSP)** adalah lapisan keamanan yang membantu mendeteksi dan mencegah berbagai serangan seperti Cross-Site Scripting (XSS) dan data injection. CSP memungkinkan administrator situs web menentukan domain mana yang dianggap sebagai sumber tepercaya untuk memuat skrip, stylesheet, gambar, dan sumber daya lainnya. aturan ini dikirimkan melalui header HTTP `Content-Security-Policy` dan diterapkan oleh browser.

Saat browser memuat halaman web, ia akan memeriksa header CSP yang dikirim oleh server. Header tersebut berisi serangkaian arahan (directives) yang mendefinisikan sumber daya apa yang boleh dimuat dan dieksekusi. Contoh arahan:
- `script-src`: menentukan sumber skrip yang valid.
- `style-src`: untuk stylesheet.
- `img-src`: untuk gambar.
- `default-src`: cadangan jika arahan spesifik tidak ditetapkan.

Browser kemudian akan memblokir semua sumber daya yang tidak sesuai dengan aturan tersebut. Misalnya, jika CSP hanya mengizinkan skrip dari domain sendiri (`script-src 'self'`), maka skrip dari domain lain atau skrip inline tidak akan dijalankan.

CSP dirancang untuk keamanan web, namun implementasi atau konfigurasi yang salah dapat membuka celah keamanan. Beberapa penyebab umum CSP dapat di-bypass:
- Mengizinkan banyak domain eksternal meningkatkan attack surface.
- Inline JavaScript bisa dieksekusi attacker.
- Nonce seharusnya random tiap request. Jika statis, attacker bisa menggunakannya kembali.
- JSONP memungkinkan eksekusi JavaScript lintas domain.
- Server yang mengirim JS dengan header tertentu bisa tetap dieksekusi walau bukan intended.
- Input user dimasukkan langsung ke DOM tanpa sanitasi.

Jika penyerang berhasil melewati CSP, mereka dapat menjalankan skrip jahat di konteks korban. Dampaknya sama dengan serangan XSS sukses:
- Mencuri cookie sesi.
- Membajak akun pengguna.
- Memodifikasi tampilan halaman (defacement).
- Menjalankan aksi atas nama korban.
- Menyebarkan malware atau mengarahkan ke situs phishing.


---

## **Percobaan Serangan di DVWA**

### **Level Low**

Pada level ini, developer menggunakan allowlist domain untuk memuat script eksternal. Sayangnya, mereka memasukkan terlalu banyak domain pihak ketiga (seperti CDN atau Pastebin) yang tidak sepenuhnya berada di bawah kendali mereka.

```PHP
$headerCSP = "Content-Security-Policy: script-src 'self' https://pastebin.com hastebin.com www.toptal.com example.com code.jquery.com https://ssl.google-analytics.com unpkg.com cdn.jsdelivr.net digi.ninja ;"; 
```

Dari header di atas, kita bisa melihat bahwa domain cdn.jsdelivr.net dan unpkg.com diizinkan. Kedua layanan ini sering digunakan untuk hosting file publik (seperti dari GitHub atau NPM). Jika penyerang menaruh script XSS di layanan tersebut, browser akan menganggapnya aman.

Kode PHP juga mengeksekusi input langsung ke dalam tag <script>:

```php
$page[ 'body' ] .= "
    <script src='" . $_POST['include'] . "'></script>
";
```

Jadi kita tidak perlu membuat tag <script> sendiri, cukup masukkan URL yang menampung file JavaScript berbahaya (XSS) yang di-host di salah satu domain yang diizinkan (misalnya jsdelivr atau unpkg).

Masukkan payload URL berikut ke dalam kolom input:
```
https://cdn.jsdelivr.net/gh/digininja/csp_bypass/alert.js
```

Klik "Include".

![Gambar-csp-bypass](assets/image/2026-02-11-csp-bypass/image1.png)

![Gambar-csp-bypass](assets/image/2026-02-11-csp-bypass/image2.png)

---

### Level Medium

Untuk level ini, terdapat arahan `nonce-TmV2ZXIgZ29pbmcgdG8gZ2l2ZSB5b3UgdXA=` yang artinya skrip inline harus memiliki atribut `nonce` dengan nilai tersebut. Nilai nonce ini **statis** (tidak berubah setiap request). Parameter `include` dimasukkan langsung ke dalam halaman tanpa encoding.

```php
<?php
$headerCSP = "Content-Security-Policy: script-src 'self' 'unsafe-inline' 'nonce-TmV2ZXIgZ29pbmcgdG8gZ2l2ZSB5b3UgdXA=';";
header($headerCSP);
header ("X-XSS-Protection: 0");
?>
```

Karena nonce tetap, kita bisa membuat skrip inline dengan menyertakan nonce yang benar. Masukkan ke form input:
   
   ```html
   <script nonce="TmV2ZXIgZ29pbmcgdG8gZ2l2ZSB5b3UgdXA=">alert('Medium Bypassed')</script>
   ```

Klik Include. Skrip akan dijalankan.
![Gambar-csp-bypass](assets/image/2026-02-11-csp-bypass/image3.png)

Hasilnya adalah script dapat dieksekusi di server
![Gambar-csp-bypass](assets/image/2026-02-11-csp-bypass/image4.png)

---

### Level High
Pada level ini, CSP terlihat sangat ketat karena hanya menggunakan 'self', yang berarti hanya script dari server DVWA itu sendiri yang boleh dijalankan. Namun, halaman ini rentan karena menggunakan mekanisme JSONP yang tidak aman. Pada JSONP, parameter callback yang dikirimkan ke server akan dipantulkan (reflected) kembali dan dieksekusi sebagai JavaScript.

```php
$headerCSP = "Content-Security-Policy: script-src 'self';";
```

Aturan ini aman, tetapi perhatikan juga bagaimana input ditangani:

```php
$page[ 'body' ] .= "
    " . $_POST['include'] . "
";
```

Karena kita memiliki fitur "Include" (seperti XSS Reflected), dan CSP mengizinkan eksekusi script dari 'self', kita dapat memanggil file PHP lokal yang rentan di DVWA (jsonp.php) dan memanipulasi parameter callback-nya.

Cara Bypass-nya adalah kita arahkan halaman web untuk memanggil script internal source/jsonp.php lalu kita kirimkan parameter callback=alert(1), server akan merespons dengan mengeksekusi alert(1). 

Gunakan Burp Suite untuk memanipulasi permintaan POST saat mengklik "Solve the sum"
ini sebelum kita edit
![Gambar-csp-bypass](assets/image/2026-02-11-csp-bypass/image5.png)

dan ini setelah kita edit bagian `callback=solveSum` menjadi `callbak=alert(1)
![Gambar-csp-bypass](assets/image/2026-02-11-csp-bypass/image6.png)

setalah itu forward saja request tadi dan lihat hasilnya
![Gambar-csp-bypass](assets/image/2026-02-11-csp-bypass/image7.png)

Browser akan memuat script tersebut. Karena asalnya dari 'self' (server DVWA itu sendiri), CSP mengizinkannya, dan XSS dieksekusi melalui pantulan callback.

### Level Impossible

Pada level Impossible, sudah ada perbaikan untuk semua celah tersebut.
+ CSP diatur secara ketat ke script-src 'self';.
+ Tidak ada parameter input yang dimasukkan mentah-mentah ke dalam DOM (body HTML).

```php
<?php

$headerCSP = "Content-Security-Policy: script-src 'self';";

header($headerCSP);

?>
<?php
if (isset ($_POST['include'])) {
$page[ 'body' ] .= "
    " . $_POST['include'] . "
";
}
$page[ 'body' ] .= '
<form name="csp" method="POST">
    <p>Unlike the high level, this does a JSONP call but does not use a callback, instead it hardcodes the function to call.</p><p>The CSP settings only allow external JavaScript on the local server and no inline code.</p>
    <p>1+2+3+4+5=<span id="answer"></span></p>
    <input type="button" id="solve" value="Solve the sum" />
</form>

<script src="source/impossible.js"></script>
';
```

Panggilan JSONP tidak lagi menggunakan parameter callback dinamis yang bisa dimanipulasi oleh user. Fungsi callback di-hardcode secara aman di sisi klien (di dalam impossible.js), sehingga menutup celah injeksi via DOM

---

## Kesimpulan
Modul CSP Bypass di DVWA menunjukkan bahwa:
- Konfigurasi CSP yang longgar (domain terlalu banyak) dapat dieksploitasi dengan hosting skrip di domain tepercaya.
- Penggunaan nonce yang statis membuka peluang penyisipan skrip inline.
- Endpoint JSONP yang tidak aman memungkinkan eksekusi kode meskipun CSP membatasi sumber skrip.

Penting bagi aplikasi untuk selalu:
- Membatasi daftar sumber hanya yang benar-benar diperlukan.
- Membangkitkan nonce secara unik dan acak setiap respons.
- Menghindari penggunaan JSONP dengan callback yang dapat dimanipulasi, atau gunakan pendekatan CORS yang lebih aman.
- Mematikan fitur tidak aman seperti `'unsafe-inline'` dan `'unsafe-eval'` kecuali benar-benar dibutuhkan.
