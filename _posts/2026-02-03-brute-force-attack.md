---
title: "DVWA : BRUTE FORCE ATTACK"
date: 2026-02-04 00.00.00
categories: [Pentest,DVWA]
tags: [brute force, cyber security, red team]
---

## Apa itu Brute Force Attack?

**Brute Force Attack** adalah serangan yang mencoba menebak kredensial (seperti password, PIN, atau kunci enkripsi) dengan cara mencoba semua kombinasi kemungkinan sampai menemukan yang benar.

Kurang lebih seperti saat kita lupa password Google. Kita akan mulai mencoba berbagai kemungkinan — tanggal lahir, nama hewan peliharaan, kombinasi nama dan angka — sampai salah satunya berhasil. Perbedaannya, peretas menggunakan tools otomatis yang bisa mencoba ratusan ribu hingga jutaan kombinasi dalam hitungan menit. Kalau berhasil, peretas bisa masuk dan mengambil alih akun tersebut.

---

## Percobaan Brute Force Attack di DVWA

DVWA (Damn Vulnerable Web Application) menyediakan modul khusus untuk mencoba serangan Brute Force ke form login yang terdiri dari kolom username dan password.

![tampilan modul brute force](/assets/image/2026-02-03-brute-force-attack/image_1.png)

Tampilan ketika login **gagal**:

![tampilan gagal login](/assets/image/2026-02-03-brute-force-attack/image_4.png)

Tampilan ketika login **berhasil**:

![tampilan berhasil login](/assets/image/2026-02-03-brute-force-attack/image_5.png)

![tampilan berhasil login 2](/assets/image/2026-02-03-brute-force-attack/image_6.png)

### Tools dan Persiapan

Tools yang digunakan adalah **Burpsuite**, yang bertugas mengirimkan kombinasi username dan password secara otomatis ke form login. Selain itu, kita perlu menyiapkan **wordlist** — yaitu daftar kata berisi kemungkinan username dan password yang akan dicoba.

**Wordlist user:**

![wordlist user](/assets/image/2026-02-03-brute-force-attack/image_2.png)

**Wordlist password:**

![wordlist password](/assets/image/2026-02-03-brute-force-attack/image_3.png)

Semua pengujian di setiap level dilakukan dengan cara dan data yang sama.


---

## Brute Force Level : Low

Dari hasil pengujian, terlihat ada 22 kombinasi username dan password yang dicoba.

![hasil brute force low](/assets/image/2026-02-03-brute-force-attack/image_7.png)

Semua percobaan mengembalikan status **200**, termasuk yang gagal login. Ini terjadi karena server selalu merespons dengan kode 200 baik login berhasil maupun tidak — server tidak membedakan keduanya lewat status HTTP. Lalu bagaimana kita tahu mana yang berhasil?

Caranya adalah dengan melihat kolom **length** (ukuran respons). Ketika login berhasil, halaman web akan menampilkan gambar profil pengguna, sehingga ukuran halamannya otomatis lebih besar dibanding halaman yang hanya menampilkan pesan gagal.

![hasil sort length low](/assets/image/2026-02-03-brute-force-attack/image_8.png)

Terlihat bahwa kombinasi **admin / password** dan **pablo / letmein** memiliki ukuran yang berbeda dari hasil lainnya — ini indikasi kuat bahwa kedua kombinasi tersebut berhasil login.

### Kenapa Level Low Sangat Rentan?

Kalau kita buka tab **View Source** di DVWA, kita bisa melihat kode PHP yang menangani proses login ini. Ada dua masalah besar di sana.

**Masalah pertama: Tidak ada sanitasi input**

```php
// Get username
$user = $_GET[ 'username' ];

// Get password
$pass = $_GET[ 'password' ];
$pass = md5( $pass );

// Check the database
$query = "SELECT * FROM `users` WHERE user = '$user' AND password = '$pass';";
$result = mysqli_query($GLOBALS["___mysqli_ston"], $query) or die(...);
```

Input dari pengguna langsung dimasukkan ke dalam query database tanpa diperiksa terlebih dahulu. Ini membuka celah untuk serangan **SQL Injection**, di mana penyerang bisa memanipulasi query-nya untuk membobol login tanpa tahu password sama sekali.

**Masalah kedua: Tidak ada Rate Limiting**

```php
if( $result && mysqli_num_rows( $result ) == 1 ) {
    // Login successful
    echo "<p>Welcome to the password protected area {$user}</p>";
    echo "<img src=\"{$avatar}\" />";
} else {
    // Login failed
    echo "<pre><br />Username and/or password incorrect.</pre>";
}
```

Tidak ada pembatasan jumlah percobaan login. Penyerang bisa mencoba sebanyak apapun tanpa hambatan — istilahnya *hajar sampai jebol*.

---

## Brute Force Level : Medium

Dari hasil pengujian, brute force tetap berhasil. Password tetap bisa dikenali, meskipun prosesnya terasa lebih lambat dari sebelumnya.

![hasil sort length medium](/assets/image/2026-02-03-brute-force-attack/image_9.png)

### Apa yang Berubah?

Di level ini, kode sudah diperbaiki di beberapa bagian (bisa dicek di tab **View Source**).

**Perbaikan pertama: Sanitasi input dengan `mysqli_real_escape_string()`**

```php
// Sanitise username input
$user = $_GET[ 'username' ];
$user = mysqli_real_escape_string($GLOBALS["___mysqli_ston"], $user);

// Sanitise password input
$pass = $_GET[ 'password' ];
$pass = mysqli_real_escape_string($GLOBALS["___mysqli_ston"], $pass);
$pass = md5( $pass );
```

Fungsi ini akan memblokir karakter-karakter khusus yang biasa dipakai untuk SQL Injection. Jadi dari sisi SQL Injection, level ini sudah lebih aman.

**Perbaikan kedua: Delay 2 detik saat login gagal**

```php
} else {
    // Login failed
    sleep( 2 );
    echo "<pre><br />Username and/or password incorrect.</pre>";
}
```

Setiap kali percobaan login gagal, server akan menunggu 2 detik sebelum merespons. Tujuannya untuk memperlambat penyerang.

### Kenapa Masih Bisa Dibobol?

Delay 2 detik memang membuat prosesnya lebih lambat, tapi **tidak menghentikan serangan sama sekali**. Burpsuite dengan pengaturan default tetap bisa mengirim request satu per satu dan menunggu respons — waktunya hanya jadi lebih lama. Selama tidak ada batas maksimum percobaan, penyerang cukup sabar dan serangan brute force masih bisa berjalan sampai selesai.

Analoginya seperti memasang palang di pintu tapi tidak menguncinya — penyerang hanya perlu lebih sabar membuka palangnya satu per satu.

---

## Brute Force Level : Impossible

Di level ini, sudah banyak perbaikan signifikan yang membuat brute force benar-benar tidak bisa berjalan.

![hasil impossible](/assets/image/2026-02-03-brute-force-attack/image_10.png)

### Perbaikan 1: Lockout Setelah 3 Kali Gagal

```php
$total_failed_login = 3;  // Maksimum percobaan gagal
$lockout_time       = 15; // Lockout dalam menit
$account_locked     = false;
```

Jika login gagal sebanyak 3 kali, akun akan dikunci selama 15 menit. Ini langsung memutus kemungkinan brute force karena penyerang tidak bisa terus mencoba tanpa batas.

### Perbaikan 2: Prepared Statement untuk Mencegah SQL Injection

```php
// Prepared statement
$data = $db->prepare('SELECT * FROM users WHERE user = (:user) AND password = (:password) LIMIT 1;');
$data->bindParam(':user', $user, PDO::PARAM_STR);
$data->bindParam(':password', $pass, PDO::PARAM_STR);
```

Dengan menggunakan PDO dan prepared statement, input pengguna tidak lagi bisa memengaruhi struktur query database. SQL Injection sepenuhnya tertutup.

Hasilnya? Semua percobaan langsung error dari awal karena akun terkunci setelah 3 kali gagal.

---

## KESIMPULAN

Brute Force Attack adalah serangan yang mencoba menebak kredensial (password, PIN, hingga kunci enkripsi) dengan cara mencoba semua kombinasi kemungkinan secara otomatis sampai menemukan yang benar.

**Level Low - Tidak Ada Perlindungan:**
Tidak ada sanitasi input (rentan SQL Injection), tidak ada rate limiting, dan server tidak membedakan respons untuk login berhasil atau gagal (hanya beda ukuran halaman). Penyerang dapat mencoba kombinasi tanpa batas sampai berhasil menemukan password.

**Level Medium - Rate Limiting Lemah:**
Input sudah disanitasi dengan `mysqli_real_escape_string()` untuk mencegah SQL Injection. Ada delay 2 detik saat login gagal untuk memperlambat serangan. Namun delay ini tidak cukup, hanya membuat serangan lebih lambat, bukan menghentikannya sama sekali.

**Level Impossible - Perlindungan Komprehensif:**
Menggunakan Account Lockout: akun dikunci 15 menit setelah 3 kali gagal login. Menggunakan Prepared Statement (PDO) untuk mencegah SQL Injection sepenuhnya. Kombinasi kedua perlindungan ini membuat brute force attack tidak bisa dijalankan.

---