---
title: "Fingerprinting Server 1"
date: 2026-02-24 00:00:00
categories: [Pentest]
tags: [cyber security, hardening, server, wstg]
---

## Intro

### Apa itu Fingerprinting?

Fingerprinting adalah proses mengidentifikasi tipe dan versi web server yang sedang berjalan pada server target. Ibarat sidik jari pada manusia, setiap web server meninggalkan "jejak" khas — baik di header HTTP, halaman error, maupun respons lain yang ia kirimkan — yang bisa digunakan untuk mengungkap identitasnya.

### Mengapa Fingerprinting Penting?

Informasi yang didapat dari fingerprinting bukan sekadar trivia teknis. Ketika seorang attacker tahu bahwa target menjalankan **Apache 2.4.66** misalnya, ia bisa langsung menelusuri database CVE untuk mencari kerentanan yang pernah ada pada versi tersebut — lalu mencoba mengeksploitasinya. Semakin spesifik informasinya, semakin terarah serangannya.

Dari sudut pandang defensive, inilah mengapa kita perlu tahu apa yang sedang "bocor" dari server kita sendiri sebelum orang lain menemukannya.

### Bagaimana Cara Kerjanya?

Ada beberapa teknik umum yang digunakan:

+ **Banner Grabbing** — Membaca header HTTP yang dikirim server untuk mengidentifikasi nama dan versi software.
+ **Error Page Analysis** — Memancing server menampilkan halaman error default yang sering kali memuat informasi teknis detail.
+ **Automated Scanning** — Menggunakan tools seperti `nmap`, `nikto`, atau ekstensi browser seperti Wappalyzer untuk otomatisasi proses ini.

### Apa yang Didapat dari Fingerprinting?

Hasil dari kegiatan ini umumnya berupa:

+ Jenis web server (Apache, Nginx, IIS, dll.)
+ Versi web server yang spesifik
+ Sistem operasi yang digunakan oleh server
+ Teknologi pendukung yang dipakai untuk membangun web (PHP, WordPress, MySQL, dsb.)

### Bagaimana Cara Mencegahnya?

Dari sisi hardening server, ada beberapa langkah yang bisa diambil:

+ **Gunakan reverse proxy** — Sembunyikan server asli di balik proxy seperti Nginx atau Cloudflare agar header asli tidak terekspos.
+ **Custom HTTP header** — Ubah atau hapus nilai header `Server` agar tidak mengungkap informasi versi.
+ **Update software secara rutin** — Meski informasi versi terbaca, setidaknya versi terbaru sudah menambal kerentanan yang diketahui.

---

## FINGERPRINTING

### HTTP Header — Apache (Default)

![contoh_header_apache_default](assets/image/2026-02-24-fingerprinting-server/image_1.png)

```http
HTTP/1.1 200 OK
Date: Tue, 24 Feb 2026 03:27:18 GMT
Server: Apache/2.4.66 (Debian)
Last-Modified: Tue, 24 Feb 2026 03:18:47 GMT
ETag: "2158-64b89588405e9-gzip"
Accept-Ranges: bytes
Vary: Accept-Encoding
Content-Length: 8536
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html
```

Dari header di atas, kita bisa langsung membaca dua informasi kritis hanya dari satu baris:

```
Server: Apache/2.4.66 (Debian)
```

Ini mengungkap **jenis web server** (Apache), **versi spesifiknya** (2.4.66), sekaligus **sistem operasi** yang menjalankannya (Debian). Ini adalah konfigurasi default Apache — tidak ada yang disembunyikan sama sekali.

---

### HTTP Header — Nginx (Default)

![contoh_header_nginx_default](assets/image/2026-02-24-fingerprinting-server/image_2.png)

```http
HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Tue, 24 Feb 2026 03:27:33 GMT
Content-Type: text/html
Last-Modified: Tue, 24 Feb 2026 03:20:51 GMT
Connection: keep-alive
ETag: W/"699d1913-2158"
Content-Length: 8536
```

Nginx secara default juga menampilkan versinya dengan jelas:

```
Server: nginx/1.22.1
```

Sedikit lebih ringkas dibanding Apache — tidak ada informasi OS di sini — tapi versi tetap terekspos. Informasi ini cukup untuk dijadikan titik awal pencarian CVE.

---

### Error Page — Apache (Default)

![contoh_error_404_apache_default](assets/image/2026-02-24-fingerprinting-server/image_3.png)

Halaman error default Apache adalah goldmine informasi. Ketika kita mengakses path yang tidak ada, Apache menampilkan halaman 404 yang secara eksplisit menyebutkan:

+ **Jenis web server** (Apache)
+ **Versi Apache** yang sedang berjalan
+ **Port** yang digunakan
+ **Nama host / OS** server

Ini lebih banyak dari yang ditampilkan header biasa. Seorang attacker bahkan tidak perlu tool khusus — cukup browser dan URL yang salah.

---

### Error Page — Nginx (Default)

![contoh_error_404_nginx_default](assets/image/2026-02-24-fingerprinting-server/image_4.png)

Nginx sedikit lebih "pelit" dibandingkan Apache. Halaman error default-nya hanya menampilkan versi Nginx yang digunakan, tanpa detail OS atau konfigurasi lain. Tetap bocor, tapi scope-nya lebih terbatas.

---

### Scan Wappalyzer

![hasil_scan_wapplyzer_apache](assets/image/2026-02-24-fingerprinting-server/image_5.png)
![hasil_scan_wapplyzer_nginx](assets/image/2026-02-24-fingerprinting-server/image_6.png)

Wappalyzer adalah ekstensi browser yang secara otomatis mendeteksi teknologi yang digunakan sebuah website hanya dengan mengunjunginya. Hasilnya konsisten dengan apa yang sudah kita temukan lewat header dan error page — tapi disajikan lebih rapi dan mudah dibaca.

Yang menarik adalah ketika kita scan website lain. Di luar sekadar web server, Wappalyzer juga bisa mendeteksi stack teknologi yang jauh lebih dalam:

![hasil_scan_wapplyzer_web_lain](assets/image/2026-02-24-fingerprinting-server/image_7.png)

Dari satu kunjungan biasa, kita bisa tahu bahwa website tersebut menggunakan **PHP**, **WordPress**, **MySQL**, **Google Analytics**, bahkan layanan seperti **Cloudflare** dan **Hostinger**. Masing-masing komponen ini punya riwayat kerentanan tersendiri yang bisa ditelusuri.

---

## KESIMPULAN

Fingerprinting adalah langkah awal dalam hampir setiap proses penetration testing dan reconnaissance. Dari kegiatan ini, kita bisa melihat bahwa informasi sensitif tentang web server — versi, OS, bahkan tech stack lengkap — sering kali tersedia secara gratis tanpa perlu eksploitasi apapun.

**Header HTTP default** dari Apache maupun Nginx sudah cukup untuk mengidentifikasi versi software yang berjalan. **Halaman error default** bahkan memberikan lebih banyak detail, terutama pada Apache. **Tools seperti Wappalyzer** membuat proses ini semakin mudah dan otomatis — cukup dengan membuka browser.

Dari sisi pertahanan, prinsipnya sederhana: **kurangi informasi yang diekspos seminimal mungkin**. Sembunyikan versi di header, matikan halaman error default, dan gunakan reverse proxy. Informasi yang tidak tersedia tidak bisa dieksploitasi.