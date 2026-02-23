---
title: "DVWA : AUTORISATION BYPASS"
date: 2026-02-06 00.00.00
categories: [Pentest]
tags: [authorisation, cyber security, red team]
---

## **Mengenai Autorisation Bypass**

Authorisation Bypass adalah kerentanan keamanan yang memungkinkan seseorang untuk mengakses halaman, fitur, atau data yang seharusnya tidak boleh mereka akses. ini bisa berdampak pada kebocoran data sensitif, manipulasi data, pengambil alihan seluruh sistem, kerugian reputasi, dan sebagainya.

Authorisation bypass bisa terjadi karena:
+ Developer Lupa Menambahkan Pengecekan
    Saat membuat fitur baru atau API endpoint, developer lupa menambahkan kode untuk memeriksa hak akses user.
+ Pengecekan Hanya di Frontend
    Kontrol akses hanya diterapkan di tampilan (UI), tapi tidak di backend/server. Penyerang bisa langsung akses API tanpa melalui UI.
+ Pengecekan Tidak Konsisten
    Halaman HTML sudah dilindungi, tapi endpoint API yang dipakai halaman tersebut tidak dilindungi.

## **Pengujian Autorisation Bypass di DVWA**

![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image1.png)

Di DVWA ada modul yang hanya bisa diakses oleh user admin yaitu modul Autorisation Bypass. Sistem ini hanya dirancang untuk diakses oleh pengguna admin, di dalamnya kita bisa melihat ada fitur untuk melihat dan mengganti nama user. Jadi, kita diminta perhatikan semua request yang dilakukan saat masuk sebagai admin, lalu coba ulangi panggilan tersebut saat masuk sebagai pengguna lain.

Untuk user kedua yang bukan admin, kita menggunakan user gordonb dengan passwordnya abc123. untuk membedakan nanti yang admin pakai bright mode dan yang user biasa pakai dark mode

### **Level Low**

Pada level Low, sistem user management hanya bisa diakses oleh admin dan user biasa tidak bisa melihatnya. 

**ini tampilan di dashboard user admin**
![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image2.png)

**ini tampilan di dashboard user gordonb**
![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image3.png)

Di dashboard admin, kita bisa lihat untuk mengakses modul Autorisation itu url-nya adalah `http://127.0.0.1:4280/vulnerabilities/authbypass/#`. 

![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image4.png)

kita coba buat akses url yang sama dari user gordonb, ternyata berhasil akses halamanya

![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image5.png)

### **Level Medium**

Pada level Medium, sudah ada penambahkan pengecekan otorisasi, tapi hanya pada halaman HTML utama. Jika user biasa mencoba akses /vulnerabilities/authbypass/, mereka akan mendapat pesan 'Unauthorised' dan HTTP 403.

gamabar saat gordonb mencoba mengakases url sebelumnya
![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image6.png)

ini terjadi karena ada penambahan kode berikut menunjukkan:

```php
if (dvwaCurrentUser() != "admin") {
    print "Unauthorised";
    http_response_code(403);
    exit;
}
?>
```

Pengecekan ini bagus, tapi sayangnya hanya diterapkan di file HTML, tidak di API-nya. Disini kita coba untuk mengakses api data endpoint tersebut

Pertama, login sebagai admin, akses halman modul authorisation bypass, dan buka Developer tools browser untuk melihat cara kerja fitur ini. Di tab network, harusnya ada request ke server untuk mengambil data semua user lalu ditampilkan seperti halaman modul

![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image7.png)

Saat halaman dimuat, kamu akan melihat ada request ke get_user_data.php. API ini yang mengambil data semua user untuk ditampilkan di halaman.

sebelumnya kita gagal untuk mengakses halaman utama modul ini, jadi disini kita coba untuk akses langsung ke API-nya `http://localhost:4280/vulnerabilities/authbypass/get_user_data.php`

![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image8.png)

sekarang kita melihat data JSON berisi informasi semua user. Meskipun halaman HTML-nya dilindungi, API-nya tidak, jadi kita tetap bisa mengambil semua data.

### **Leve High**

Pada level High, developer sudah belajar dari kesalahan di level Medium. Sekarang baik halaman HTML maupun API get_user_data.php sudah dilindungi dengan pengecekan otorisasi. Tapi, kita masih belum coba fitur edit data user di modul tersebut. tapi sebelumnya kita coba lagi untuk endpoit `/vulnerabilities/authbypass/` dan `/vulnerabilities/authbypass/get_user_data.php` oleh user gordonb

![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image9.png)
![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image10.png)

Kedua endpoint tersebut sudah tidak bisa kita akses lagi ya dari user gordonb. Next kita coba fitur lain di sistem user management ini yaitu fungsi untuk mengubah data user. 

Kita cari endpoint untuk update data itu.
Pertama, Login sebagai admin, buka halaman Authorisation Bypass, lalu buka Developer Tools dan buka Tab Network.

![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image11.png)

Selanjutnya coba ubah nama depan atau nama belakang salah satu user, lalu klik Update. Di Network tab, kita akan melihat ada POST request ke change_user_details.php dengan payload JSON seperti ini:

```json
{
  "first_name": "Bob",
  "id": 5,
  "surname": "Marley"
}
```
![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image12.png)
![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image13.png)

Sekarang dari user gordonb kita coba mengirim POST request manual. Caranya kita buka developer console lalu jalankan kode JS berikut :

```javascript
fetch('/vulnerabilities/authbypass/change_user_details.php', {
  method: 'POST',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    'id': 1,
    "first_name": "Hacked",
    "surname": "ByGordon"
  })
})
.then((response) => response.json())
.then((data) => console.log(data));
```
![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image14.png)

Request berhasil, kita baru saja mengubah nama admin (user id=1) menjadi 'Hacked ByGordon' padahal login sebagai user biasa.
Verifikasi dengan login sebagai admin lagi, dan kamu akan lihat namanya sudah berubah.

![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image15.png)

### **Level Impossible**

Pada level Impossible, semua endpoint sudah dilindungi dengan benar. Setiap request (baik GET maupun POST) akan memeriksa apakah user yang sedang login adalah admin atau bukan. Jika bukan admin, request akan langsung ditolak.

Sekarang kita coba test semua endpoint sebagai user biasa (gordonb):

+ coba /vulnerabilities/authbypass/ dan hasilnua adalah Ditolak
![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image16.png)

+ coba get_user_data.php dan hasilnya Ditolak 
![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image17.png)

+ change_user_details.php dan hasilnya Ditolak 
![Gambar_DVWA](/assets/image/2026-02-13-auth-bypass/image18.png)

Semua endpoint sudah dilindungi dengan benar. Tidak ada cara untuk bypass otorisasi pada level ini.