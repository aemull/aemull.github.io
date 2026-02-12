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

DVWA (Damn Vulnerable Web Application) menyediakan modul Insecure CAPTCHA dengan empat level keamanan: Low, Medium, High, dan Impossible. Tujuan kita adalah untuk mengganti password user sekarang secara otomatis. Berikut adalah analisis detail untuk setiap level:

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

**2**. step 2 untuk update password

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

jadi untuk bypass nya cukup dengan mengirim http request 

