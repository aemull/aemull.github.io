---
title: XSS STORED
date: 2026-02-04 00.00.00
categories: [Pentest]
tags: [XSS, cyber security, red team]
---

XSS Stored (Persistent XSS) adalah jenis serangan Cross-Site Scripting di mana skrip berbahaya yang disuntikkan oleh penyerang disimpan secara permanen di server aplikasi web (misalnya di database, komentar, forum, profil pengguna, dll.), dan kemudian dieksekusi otomatis ketika korban mengakses halaman yang menampilkan data tersebut.

## **Cara Kerja XSS Stored:**
* Penyerang menyuntikkan skrip berbahaya (biasanya JavaScript) ke dalam aplikasi web yang menyimpan data input pengguna.
* Server menyimpan input berbahaya tersebut di database tanpa validasi atau sanitasi yang memadai.
* Korban mengakses halaman yang menampilkan data tersebut (misalnya halaman forum, komentar, atau profil).
* Skrip berbahaya dieksekusi di browser korban, seolah-olah itu bagian legit dari halaman web.
* Skrip dapat mencuri cookie, token sesi, mengirim permintaan atas nama korban, atau mengubah konten halaman.

## **Dampak:**
* Pencurian sesi (session hijacking)
* Pencurian data pribadi
* Defacement (pengubahan tampilan situs)
* Redirect ke situs phishing
* Keylogging (pencatatan ketikan)

Perbedaan dengan XSS Lain:
Reflected XSS: Skrip tidak disimpan, tetapi dipantulkan langsung dari input URL/permintaan
DOM-based XSS: Kerentanan ada di sisi klien (JavaScript), bukan server
Stored XSS: Paling berbahaya karena memengaruhi semua pengguna yang mengakses konten terinfeksi

## **Cara Mencegah:**
* Validasi dan sanitasi input (whitelist karakter yang diizinkan)
* Escape output (HTML encoding sebelum menampilkan data)
* Content Security Policy (CSP)
* HttpOnly flag pada cookie
* Framework modern yang memiliki proteksi XSS bawaan

Catatan: XSS Stored dianggap paling berbahaya karena skrip berjalan otomatis untuk semua pengguna yang mengakses konten yang terinfeksi, tanpa memerlukan interaksi langsung dengan penyerang.