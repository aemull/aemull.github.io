---
title: FILE INCLUTION
date: 2026-02-06 00.00.00
categories: [Pentest]
tags: [File Inclution, cyber security, red team]
---

# **Apa itu File Inclusion**

File Inclusion adalah kerentanan yang memungkinkan penyerang memasukkan file (biasanya kode PHP) ke dalam aplikasi web yang sedang berjalan. Terdapat dua jenis:

* Local File Inclusion (LFI): Menyertakan file dari server yang sama
* Remote File Inclusion (RFI): Menyertakan file dari server eksternal via URL

cara kerjanya itu aplikasi web mengambil parameter (misal ?page=home.php) dan menyertakan file tersebut tanpa validasi yang memadai. Penyerang bisa memanipulasi parameter untuk mengarah ke file lain.

Contoh:

```
http://target.com/index.php?page=../../etc/passwd
```

Dampak dari kerentanan ini :

* Membaca file sensitif: /etc/passwd, file konfigurasi, source code
* Eksekusi kode: Jika bisa upload file atau ada file log yang bisa dikontrol
* RFI lebih berbahaya: Penyerang bisa jalankan kode PHP sepenuhnya dari server mereka

# **Percobaan File Inclussion di DVWA**

![tampilan_dvwa_file_inclution](/assets/2026-02-06-file-inclusion/image1.png)

Di DVWA disediakan modul File Inclution yang bisa dieskploitasi dengan 4 tingkat kesulitan

## **Level Low**

Pertama kita lihat dari source code, terlihat bahwa tidak ada sama sekali filter

```PHP
<?php

// The page we wish to display
$file = $_GET[ 'page' ];

?>
```

Percobaan pertama dilakukan dengan mencoba mengakses file passwd di direktori etc. Untuk menemukan path ke file passwd digunakan directory traversal untuk membaca file sistem. dan hasilnya ditemukan pathnya sebagai berikut

```
http://localhost:4280/vulnerabilities/fi/?page=../../../../../../etc/passwd
```

![tampilan_dvwa_file_inclution](/assets/2026-02-06-file-inclusion/image2.png)

dan hasilnya terlihat paling atas bahwa file passwd bisa dilihat oleh user

atau juga bisa pakai php stream dengan contoh parameternya adalah `?page=data://text/plain,<?php%20phpinfo();?>`

![tampilan_dvwa_file_inclution](/assets/2026-02-06-file-inclusion/image5.png)


## **Level Medium**

Untuk level medium terlihat sudah diberikan beberapa pengamanan dengan menambahkan balcklist untuk parameter berisi url dan path travelsal. Namun cara balclist seperti ini masih bisa diakali dengan cara mengganti pattern dari parameternya saja.

```PHP
$file = str_replace( array( "http://", "https://" ), "", $file );
$file = str_replace( array( "../", "..\"" ), "", $file );

```

contoh parameter yang bisa digunakan adalah seperti `?page=....//....//....//....//....//....//etc/passwd` yang jika sudah filter berubah menjadi `?page=../../../../../../etc/passwd` dan bisa dieksekusi oleh server

![tampilan_dvwa_file_inclution](/assets/2026-02-06-file-inclusion/image3.png)

dan hasilnya terlihat paling atas untuk file passwd

## **Level High**

Untuk level high terlihat lebih baik karena hanya parameter dengan awalan "*file*" dan file *include.php* saja yang bisa dijalankan. namun jika hanya mengandalkan "file*" saja bisa jadi ada file lain yang memiliki prefix yang sama atau inputan parameter dengan awalan "file".

```PHP
if( !fnmatch( "file*", $file ) && $file != "include.php" ) {
    echo "ERROR: File not found!";
    exit;
}
```

contohnya dengan parameter `?page=file/../../../../../../etc/passwd`. Kode PHP akan membaca awalan parameter dan cocok, selanjutnya function `include($file)` akan memprosessnya untuk diimport dan dieksekusi.

![tampilan_hasil_High](/assets/2026-02-06-file-inclusion/image4.png)

Hasilnya terlihat bahwa isi file passwd bisa ditampilkan

## **Level Impossible**

Untuk level imposible sudah menerapkan pendekan yang benar untuk mengatasi file inclusion diantaranya 

* whitelist eksplisit
* hanya file tertentu
* tidak tergantung pattern
* tidak bisa traversal
* tidak bisa remote include


```PHP
if( $file != "include.php" && 
    $file != "file1.php" && 
    $file != "file2.php" && 
    $file != "file3.php" )
{
    echo "ERROR: File not found!";
    exit;
}
```
dari hasil percobaan menggunakan path travelsal dan remote include pun tidak membuahkan hasil apapun

![hasli_impossible1](/assets/2026-02-06-file-inclusion/image6.png)
![hasli_impossible1](/assets/2026-02-06-file-inclusion/image7.png)

dan saat menggunakan stream juga hasilnya tetap sama

![hasli_impossible1](/assets/2026-02-06-file-inclusion/image8.png)

jadi untuk pendekatan menggunakan wirhlist yang jelas ini sudah bisa menangani dari file inclution
