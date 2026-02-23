---
title: "DVWA : COMMAND INJECTION"
date: 2026-02-04 00.00.00
categories: [Pentest,DVWA]
tags: [command injection, cyber security, red team]
---

## **INTRO**

**Command Injection** adalah sebuah kerentanan keamanan pada aplikasi web yang memungkinkan penyerang untuk mengeksekusi perintah sistem operasi secara sewenang-wenang pada server yang menjalankan aplikasi tersebut.

Kerentanan ini terjadi karena aplikasi menerima input dari pengguna (misalnya, melalui form web, cookie, atau header HTTP) dan menganggapnya aman sebagai bagian dari perintah sistem yang akan dieksekusi oleh server. Tidak hanya memproses data yang dimaksudkan, aplikasi juga mempercayai input tersebut dan meneruskannya ke shell sistem operasi tanpa melakukan validasi atau sanitasi yang baik.

**Dampak jika kerentanan ini dieksploitasi** bisa sangat berbahaya, antara lain:

1. Penyerang dapat membaca file-file sensitif di server, seperti file konfigurasi database, kode sumber aplikasi, atau data pengguna.
2. Penyerang dapat mengubah atau menghapus file di server, yang dapat merusak integritas aplikasi dan data.
3. Penyerang dapat mengunggah backdoor atau shell (misalnya, reverse shell) untuk mendapatkan kendali penuh atas server.
4. Server yang berhasil dikompromikan dapat digunakan sebagai titik awal untuk menyerang sistem lain di dalam jaringan internal.
5. Penyerang dapat menjalankan perintah yang menghabiskan sumber daya server, seperti fork bomb, sehingga server menjadi tidak responsif.

Eksploitasi ini memanfaatkan karakter khusus shell seperti `&&`, `|`, `;`, dan lainnya untuk menyisipkan perintah berbahaya.

---

## **Percobaan Serangan di DVWA**

Aplikasi DVWA memiliki fitur "Ping", yang meminta pengguna memasukkan alamat IP, kemudian server akan melakukan perintah `ping` ke IP tersebut. Fitur inilah yang akan kita uji.

### **Level Low**

Pada level ini, kode PHP sama sekali tidak melakukan validasi atau filtering terhadap input pengguna. Input dari `$_REQUEST['ip']` langsung digabungkan ke dalam perintah `shell_exec`.

```php
$target = $_REQUEST[ 'ip' ];
// ...
$cmd = shell_exec( 'ping  -c 4 ' . $target );
```
Pengguna dapat memasukkan apa pun, dan itu akan dieksekusi sebagai bagian dari perintah sistem.

Kita coba untuk masukkan alamat IP, lalu tambahkan karakter pemisah perintah diikuti dengan perintah yang ingin dijalankan. Contoh: 

```
127.0.0.1; whoami
```
![gambar_masukin_syntak](assets/image/2026-02-03-command-injection/image2.png) 

Di sini, urutan eksekusi yang terjadi di server adalah: `ping -c 4 127.0.0.1; whoami`. Titik koma (`;`) memungkinkan penyerang untuk menjalankan perintah kedua (`whoami`) setelah perintah pertama (`ping`) selesai, terlepas dari keberhasilan perintah pertama.

![output_ping](assets/image/2026-02-03-command-injection/image1.png)

Output dari perintah `ping` akan ditampilkan, diikuti oleh output dari perintah `whoami` yang menghasilkan `www-data`. Ini membuktikan bahwa kita berhasil mengeksekusi perintah tambahan.


### **Level Medium**

Di level medium, terilahat pada aplikasi ping melakukan filtering dengan membuat **blacklist** sederhana dengan mengganti string `&&` dan `;` menjadi string kosong.

```php
$substitutions = array(
    '&&' => '',
    ';'  => '',
);
$target = str_replace( array_keys( $substitutions ), $substitutions, $target );
```

Namun, pendekatan blacklist ini sangat lemah. Penyerang dapat dengan mudah mencari cara untuk melewatinya. Salah satu caranya adalah dengan mengganti operator `&&` dan `;` dengan operator yang tidak difilter, misal `&` dan `|`.

Disini kita akan coba dengan menggunakan operator pipe `|` pada payloadnya
```
127.0.0.1 | pwd
```

![output_ping](assets/image/2026-02-03-command-injection/image3.png)

dan hasilnya akan menampilkan direkotry aktif di server yaitu `/var/www/html/vulnerabilities/exec`
![output_ping](assets/image/2026-02-03-command-injection/image4.png)

### **Level High**

Di level high, untuk memperluas blacklist ditambahkan lebih banyak karakter dan operator yang berbahaya.
```php
$substitutions = array(
    '||' => '',
    '&'  => '',
    ';'  => '',
    '| ' => '', //   <-- Perhatikan spasi setelah '|'
    '-'  => '',
    '$'  => '',
    '('  => '',
    ')'  => '',
    '`'  => '',
);
$target = str_replace( array_keys( $substitutions ), $substitutions, $target );
```

Sekilas terlihat lebih aman. Namun, ada kelemahan fatal di sini, yaitu pada elemen `'| '`. Blacklist ini hanya menghapus karakter pipe jika **diikuti oleh spasi** (`| `). Jika pipe tidak diikuti spasi, maka tidak akan terfilter. Selain itu, fungsi `trim()` hanya menghapus spasi di awal dan akhir string, bukan di tengah.

Kita akan coba memanfaatkan cerlah tersebut dengan memasukan payload dengan `|` tapi tanpa spasi seperti berikut
```bash
127.0.0.1|ls
```
![output_ping](assets/image/2026-02-03-command-injection/image5.png)
Karena string `| ` (pipe+spasi) tidak ditemukan, filter tidak akan menghapus apapun. Perintah `whoami` akan dieksekusi dengan outputnya dikirimkan melalui pipe ke perintah selanjutnya (yang tidak ada), sehingga output akan tetap muncul di layar.

![output_ping](assets/image/2026-02-03-command-injection/image6.png)
Eksploitasi berhasil.

### **Level Impossible**

Di level ini, pendekatan berubah total dari **blacklist** menjadi **whitelist**. Developer tidak lagi mencoba menghapus karakter berbahaya, tetapi **memvalidasi input dengan sangat ketat** untuk memastikan input tersebut sesuai dengan format yang diharapkan.

```php
$octet = explode( ".", $target );
if( ( is_numeric( $octet[0] ) ) && ( is_numeric( $octet[1] ) ) && ( is_numeric( $octet[2] ) ) && ( is_numeric( $octet[3] ) ) && ( sizeof( $octet ) == 4 ) ) {
    $target = $octet[0] . '.' . $octet[1] . '.' . $octet[2] . '.' . $octet[3];
    // ... execute ping
```

Disini input IP dipecah menjadi 4 bagian berdasarkan titik (`.`). Kemudian, kode memeriksa apakah setiap bagian adalah **numerik** dan apakah jumlah bagiannya **tepat 4**. Ini berarti pengguna **hanya bisa** memasukkan angka dan titik dalam format IP yang valid (misal, 192.168.1.1).

Setelah divalidasi, keempat oktet digabungkan kembali. Proses ini memastikan tidak ada karakter berbahaya yang lolos.

Tidak ada celah untuk melakukan Command Injection di level ini. Input selain angka dan titik (dalam format IP yang benar) akan langsung ditolak dan menghasilkan pesan error. Kode tidak akan pernah sampai ke fungsi `shell_exec` dengan input yang tidak valid.

![output_ping](assets/image/2026-02-03-command-injection/image7.png)
![output_ping](assets/image/2026-02-03-command-injection/image8.png)

---

## KESIMPULAN


Command Injection adalah kerentanan yang memungkinkan penyerang mengeksekusi perintah sistem operasi sewenang-wenang melalui input yang tidak divalidasi, karena aplikasi menganggap input pengguna aman dan langsung meneruskannya ke shell sistem.

**Level Low - Tanpa Validasi:**
Tidak ada filtering atau validasi sama sekali. Input langsung digabungkan ke perintah shell. Penyerang dapat menggunakan karakter pemisah perintah seperti `;`, `&&`, atau `|` untuk menjalankan perintah tambahan.

**Level Medium - Blacklist Lemah:**
Menggunakan blacklist untuk menghapus karakter berbahaya seperti `&&` dan `;`. Namun pendekatan ini mudah diobati dengan menggunakan operator alternatif seperti `|` yang tidak difilter.

**Level High - Blacklist yang Lebih Panjang:**
Blacklist diperluas untuk mencakup lebih banyak karakter berbahaya. Namun masih ada celah kecil, misalnya filtering `| ` (pipe+spasi) tetapi tidak `|` (pipe tanpa spasi), sehingga penyerang masih bisa melewatinya dengan manipulasi format input.

**Level Impossible - Whitelist Validation:**
Menggunakan pendekatan whitelist yang ketat, hanya menerima input yang sesuai format IP yang valid (empat angka dipisahkan titik). Setiap bagian divalidasi untuk memastikan numerik. Ini adalah cara yang paling aman karena tidak membiarkan karakter berbahaya sama sekali.


