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

Kita coba untuk masukkan alamat IP, lalu tambahkan karakter pemisah perintah diikuti dengan perintah yang ingin dijalankan. Contoh: `127.0.0.1; whoami`
  
Di sini, urutan eksekusi yang terjadi di server adalah: `ping -c 4 127.0.0.1; whoami`. Titik koma (`;`) memungkinkan penyerang untuk menjalankan perintah kedua (`whoami`) setelah perintah pertama (`ping`) selesai, terlepas dari keberhasilan perintah pertama.

Output dari perintah `ping` akan ditampilkan, diikuti oleh output dari perintah `whoami`. Ini membuktikan bahwa kita berhasil mengeksekusi perintah tambahan.


#### **Level Medium**

*   **Analisis Kode:**
    Developer mencoba melakukan filtering dengan membuat **blacklist** sederhana. Developer mengganti string `&&` dan `;` menjadi string kosong.

    ```php
    $substitutions = array(
        '&&' => '',
        ';'  => '',
    );
    $target = str_replace( array_keys( $substitutions ), $substitutions, $target );
    ```

    Namun, pendekatan blacklist ini sangat lemah. Penyerang dapat dengan mudah mencari cara untuk melewatinya.

*   **Eksploitasi:**
    1.  Karena `&&` dihapus, kita bisa menggunakan operator lain seperti `&` atau `|`.
    2.  Operator `&` tidak difilter. Coba payload: `127.0.0.1 & whoami`
    3.  Operator `|` juga tidak difilter. Coba payload: `127.0.0.1 | whoami`
    4.  Selain itu, karakter seperti `;` dihapus, tetapi terkadang filtering hanya dilakukan sekali. Coba gunakan payload dengan karakter yang tidak ada dalam blacklist, seperti newline (`%0a`) yang dalam URL encoding setara dengan baris baru.
        *   Payload (di URL setelah submit): `127.0.0.1%0awhoami` (cara ini mungkin lebih efektif jika aplikasi menerima newline sebagai pemisah perintah).

*   **Hasil:**
    Payload `127.0.0.1 | whoami` akan berhasil, sama seperti di level Low. Ini menunjukkan bahwa blacklist parsial tidak cukup untuk mengamankan aplikasi.

#### **Level High**

*   **Analisis Kode:**
    Developer memperluas blacklist dengan menambahkan lebih banyak karakter dan operator yang berbahaya.

    ```php
    $substitutions = array(
        '||' => '',
        '&'  => '',
        ';'  => '',
        '| ' => '', // Perhatikan spasi setelah '|'
        '-'  => '',
        '$'  => '',
        '('  => '',
        ')'  => '',
        '`'  => '',
    );
    $target = str_replace( array_keys( $substitutions ), $substitutions, $target );
    ```

    Sekilas terlihat lebih aman. Namun, ada kelemahan fatal di sini, yaitu pada elemen `'| '`. Blacklist ini hanya menghapus karakter pipe jika **diikuti oleh spasi** (`| `). Jika pipe tidak diikuti spasi, maka tidak akan terfilter.

    Selain itu, fungsi `trim()` hanya menghapus spasi di awal dan akhir string, bukan di tengah.

*   **Eksploitasi:**
    1.  Kita manfaatkan celah pada filter `'| '`. Kita akan menggunakan pipe, tetapi tanpa spasi setelahnya.
    2.  Coba payload: `127.0.0.1|whoami` (tanpa spasi setelah pipe).
    3.  Karena string `| ` (pipe+spasi) tidak ditemukan, filter tidak akan menghapus apapun. Perintah `whoami` akan dieksekusi dengan outputnya dikirimkan melalui pipe ke perintah selanjutnya (yang tidak ada), sehingga output akan tetap muncul di layar.

*   **Hasil:**
    Eksploitasi berhasil. Ini adalah contoh sempurna bagaimana sebuah kesalahan kecil (typographical error) dalam pembuatan blacklist dapat membuat seluruh pertahanan menjadi tidak berguna.

#### **Level Impossible**

*   **Analisis Kode:**
    Di level ini, pendekatan berubah total dari **blacklist** menjadi **whitelist**. Developer tidak lagi mencoba menghapus karakter berbahaya, tetapi **memvalidasi input dengan sangat ketat** untuk memastikan input tersebut sesuai dengan format yang diharapkan.

    1.  **Anti-CSRF Token:** Kode dilindungi dengan token CSRF untuk mencegah serangan yang memanfaatkan sesi pengguna yang sah.
    2.  **Validasi Ketat:** Input IP dipecah menjadi 4 bagian berdasarkan titik (`.`). Kemudian, kode memeriksa apakah setiap bagian adalah **numerik** dan apakah jumlah bagiannya **tepat 4**. Ini berarti pengguna **hanya bisa** memasukkan angka dan titik dalam format IP yang valid (misal, 192.168.1.1).
    3.  **Rekonstruksi Aman:** Setelah divalidasi, keempat oktet digabungkan kembali. Proses ini memastikan tidak ada karakter berbahaya yang lolos.

    ```php
    $octet = explode( ".", $target );
    if( ( is_numeric( $octet[0] ) ) && ( is_numeric( $octet[1] ) ) && ( is_numeric( $octet[2] ) ) && ( is_numeric( $octet[3] ) ) && ( sizeof( $octet ) == 4 ) ) {
        $target = $octet[0] . '.' . $octet[1] . '.' . $octet[2] . '.' . $octet[3];
        // ... execute ping
    ```

*   **Eksploitasi:**
    **Tidak Mungkin.** Tidak ada celah untuk melakukan Command Injection di level ini. Input selain angka dan titik (dalam format IP yang benar) akan langsung ditolak dan menghasilkan pesan error. Kode tidak akan pernah sampai ke fungsi `shell_exec` dengan input yang tidak valid.

### **Kesimpulan**

Modul Command Injection di DVWA dengan sangat baik mengilustrasikan evolusi kerentanan dan perbaikannya.

*   **Low Level** menunjukkan bahaya dari **tanpa validasi** sama sekali.
*   **Medium Level** menunjukkan bahwa **blacklist parsial** mudah dilewati.
*   **High Level** menunjukkan bahwa **blacklist yang tidak sempurna** (human error) juga tidak cukup dan bisa dilewati.
*   **Impossible Level** menunjukkan bahwa **whitelist dengan validasi ketat** adalah pertahanan yang paling efektif untuk mencegah serangan Command Injection. Prinsip utamanya adalah: "Jangan percaya apapun dari pengguna." Selalu validasi input agar sesuai dengan apa yang diharapkan (format IP, email, angka, dll.), bukan hanya mencoba menghapus apa yang dianggap berbahaya.