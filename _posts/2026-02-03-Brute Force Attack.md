---
title: Brute Force Attack
date: 2026-02-04 00.00.00
categories: [Pentest]
tags: [brute force, cyber security, red team]
---


# **BRUTE FORCE ATTCAK**

## Apa itu Brute Force Attack ?

***Brute Force Attack*** adalah serangan yang mencoba menebak kredensial (seperti password, pin, atau kunci enkripsi) dengan cara mencoba semua kombinasi kemungkinan sampai menemukan yang benar.

Kurang lebih seperti saat kita ingin login ke google tapi lupa kata sandinya. Disitu kita akan mencoba berbagai kemungkinan password yang bener, mulai dari mencoba input tanggal lahir, alamat, kombinasi tanggal lahir sama nama, kombinasi nama presiden dan mentri, semua kombinasi kalimat yang ada di kepala kita dicoba sampai bisa login.

Peretas biasanya menggunakan tools otomatis agar bisa melakukan input ratusan ribu hingga jutaan kombinasi kalimat dalam waktu yang cepat. Kalau misal peretas itu berhasil menebak password, maka peretas bisa masuk menggunakan akun tersebut dan bisa juga menganmbil alih akun tersebut (*akunnya dicuri*).

## Percobaan Brute Force Attack Di DVWA

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_1.png)

Di DVWA ada modul untuk mencoba serangan Brute Force ke form login yang terdiri dari username dan password. selanjutnya kita akan mecoba setiap level untuk melihat celah keamananya

untuk tampilan jika gagal login seperti berikut

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_4.png)

untuk tampilan jika berhasil login seperti berikut

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_5.png)

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_6.png)

untuk tools yang digunakan adalah Burpsuite, yang nantinya akan melakukan input otomatis username dan password kedalam webnya. selain itu kita harus menyiapkan daftar kata (wordlist) password dan user yang akan dimasukan ke form login

**wordlist user**

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_2.png)

**wordlist password**

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_3.png)

untuk pengujian disemua level dilakukan dengan cara dan data yang sama

#### Bruter Force Level : Low

Dari hasil pengujian, terlihat ada 22 pengujian kombinasi pasword

![tampilan_Hasil_brutfece](/assets/image/2026-02-03-Brute_Force_Attcak/image_7.png)

karena semua status *200 (Success)*, maka salah satu cara untuk melihat keberhasilannya adalah dari *lengt*, karena jiga berhasil login halaman web akan menampilkan gambar yang secara tidak langsung ukuran *lengt* nya juga lebih besar

![hasil_sort_lengt](/assets/image/2026-02-03-Brute_Force_Attcak/image_8.png)

terlihat bahwa kombinasi ***admin*** dengan ***password*** dan ***pablo*** dengan ***letmein*** memiliki ukuran yang berbeda dari hasil lainnya, ini bisa dijadikan indikasi bahwa password tersebut benar 

Bisa dilihat kode di atas tidak memiliki sanitasi sama sekali dalam inputa `$user` dan `$pass`. Hal tersebut bisa dijadikan sebagai celah untuk melakukan *SQL Injection* karena data langsung dimasukan kedalam query. berikut kode yang rentannya

```
    // Get username
    $user = $_GET[ 'username' ];

    // Get password
    $pass = $_GET[ 'password' ];
    $pass = md5( $pass );

    // Check the database
    $query  = "SELECT * FROM `users` WHERE user = '$user' AND password = '$pass';";
    $result = mysqli_query($GLOBALS["___mysqli_ston"],  $query ) or die( '<pre>' . ((is_object($GLOBALS["___mysqli_ston"])) ? mysqli_error($GLOBALS["___mysqli_ston"]) : (($___mysqli_res = mysqli_connect_error()) ? $___mysqli_res : false)) . '</pre>' );
```

hal lainnya adalah tidak adanya penerapan *Rate Limit*, atau batasan jumlah request login dalam jangka waktu tertentu. ini bisa mempermudah penyerang untuk melakukan brute force dengan jumlah bercobaan berapapun (*pokonya hajar sampai jebol*). berikut kodenya

 if( $result && mysqli_num_rows( $result ) == 1 ) {
        // Get users details
        $row    = mysqli_fetch_assoc( $result );
        $avatar = $row["avatar"];

        // Login successful
        echo "<p>Welcome to the password protected area {$user}</p>";
        echo "<img src=\"{$avatar}\" />";
    }
    else {
        // Login failed
        echo "<pre><br />Username and/or password incorrect.</pre>";
    }

    ((is_null($___mysqli_res = mysqli_close($GLOBALS["___mysqli_ston"]))) ? false : $___mysqli_res);

#### Brute Force Level : Medium

dari hasilnya tetap sama, password berhasil dikenali dan proses brute force berjalan lancar meskipun tidak secepat sebelumnya.

![hasil_short_lengt_medium](/assets/image/2026-02-03-Brute_Force_Attcak/image_9.png)

kalau dilihat dari sruktur kodenya, sudah ditambahkan `mysqli_real_escape_string()` untuk mencegah adanya carater selain aphabet dan number masuk. jadi lebih aman dari serangan sql injection

```
// Sanitise username input
    $user = $_GET[ 'username' ];
    $user = ((isset($GLOBALS["___mysqli_ston"]) && is_object($GLOBALS["___mysqli_ston"])) ? mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $user ) : ((trigger_error("[MySQLConverterToo] Fix the mysql_escape_string() call! This code does not work.", E_USER_ERROR)) ? "" : ""));

    // Sanitise password input
    $pass = $_GET[ 'password' ];
    $pass = ((isset($GLOBALS["___mysqli_ston"]) && is_object($GLOBALS["___mysqli_ston"])) ? mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $pass ) : ((trigger_error("[MySQLConverterToo] Fix the mysql_escape_string() call! This code does not work.", E_USER_ERROR)) ? "" : ""));
    $pass = md5( $pass );
```

Dan bisa dilihat juga sudah menerapkan sleep selama 2 detik untuk percobaan login yang gagal

```
    else {
        // Login failed
        sleep( 2 );
        echo "<pre><br />Username and/or password incorrect.</pre>";
    }
```

walapun ada perbaikan tapi belum cukup untuk mencegah adanya brute force

#### Brute Force level : Immposible

untuk yang level imposible itu sudah banyak perbaikannya. Mulai dari pembatasan percobaan login sebanyak 3 kali gagal, jika sudah melewati batas tersebut maka akun akan terkunci tidak bisa login selama 15 menit

```
$total_failed_login = 3;    // Maksimum percobaan gagal
$lockout_time       = 15;   // Lockout dalam menit
$account_locked     = false;
```

![hasil_short_lengt_medium](/assets/image/2026-02-03-Brute_Force_Attcak/image_10.png)

sudah ditambahkan juga PDO untuk menjegah dari serangan SQL Injection

```
// Prepared statement
$data = $db->prepare( 'SELECT * FROM users WHERE user = (:user) AND password = (:password) LIMIT 1;' );
$data->bindParam( ':user', $user, PDO::PARAM_STR);
$data->bindParam( ':password', $pass, PDO::PARAM_STR );
```

dan untuk percobaannya terhenti dari awal jadi semuanya error.