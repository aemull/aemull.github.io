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

Mencoba Menebak password atau pin seperti diatas sudah termasuk kedalam serangan brute force, tapi untuk para peretas biasanya menggunakan tools otomatis agar bisa melakukan input ratusan ribu hingga jutaan kombinasi kalimat dalam waktu yang cepat. Kalau misal peretas itu berhasil menebak password, maka peretas bisa masuk menggunakan akun tersebut dan bisa juga menganmbil alih akun tersebut (*akunnya dicuri*).

## Percobaan Brute Force Attack Di DVWA

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_1.png)

Di DVWA ada modul untuk mencoba serangan Brute Force ke form login yang terdiri dari username dan password. selanjutnya kita akan mecoba setiap level untuk melihat celah keamananya

untuk tampilan jika gagal login seperti berikut

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_4.png)

untuk tampilan jika berhasil login seperti berikut

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_5.png)

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_6.png)

untuk tools yang digunakan adalah Burpsuite yang nanti nya akan melakukan input otomatis username dan password kedalam webnya. selain itu harus menyiapkan daftar kata (wordlist) password dan user yang akan dimasukan ke form login

wordlist user

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_2.png)

wordlist password

![tampilan modul brute force](/assets/image/2026-02-03-Brute_Force_Attcak/image_3.png)

untuk cara kerjanya nanti burpsuite akan 

#### Bruter Force Level : Low

Dari hasil pengujian, terlihat terjadi 22 pengujian kombinasi pasword

![tampilan_Hasil_brutfece](/assets/image/2026-02-03-Brute_Force_Attcak/image_hasil.png)