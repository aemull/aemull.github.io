---
title: JAVASCRIPT ATTCAK
date: 2026-02-13 00.00.00
categories: [Pentest]
tags: [javascript, cyber security, red team]
---

## **INTRO**

### **Apa itu JavaScript?**
JavaScript adalah bahasa pemrograman yang terutama digunakan untuk membuat halaman web menjadi interaktif dan dinamis. Berbeda dengan PHP yang berjalan di server (server-side), JavaScript biasanya dieksekusi langsung di browser pengguna (client-side). Ini memungkinkan halaman web untuk merespon tindakan pengguna, memanipulasi tampilan, dan berkomunikasi dengan server tanpa perlu memuat ulang halaman.

### **Apa Penyebab JavaScript Rentan?**
Kerentanan pada JavaScript bisa muncul karena satu alasan utama: **kode sepenuhnya berada di bawah kendali pengguna**. Karena kode dikirim ke browser, pengguna yang jahat dapat:
1.  **Melihatnya**: Tidak ada kode client-side yang benar-benar tersembunyi.
2.  **Memanipulasinya**: Mengubah nilai variabel, memanggil fungsi, atau menghentikan eksekusi script.
3.  **Menggantinya**: Menggunakan ekstensi browser atau fitur Developer Tools untuk mengedit script secara langsung atau menggantinya dengan script lain.

### **Apa Hal yang Ditimbulkan Jika JavaScript Dieksploitasi?**
Eksploitasi JavaScript (client-side) dalam konteks DVWA ini biasanya mengarah pada:
*   **Bypass Keamanan**: Melewati mekanisme validasi input atau pembuatan token yang seharusnya memastikan pengguna mengirim data yang benar.
*   **Reverse Engineering**: Memahami algoritma yang digunakan untuk melindungi suatu data, lalu mereproduksinya secara manual.
*   **Manipulasi Data**: Mengubah data yang dikirim ke server agar sesuai dengan yang diinginkan penyerang.


---

## PERCOBAAN SERANGAN DI DVWA

### **Level Low**

Pada level Low, tujuan utama kita adalah agar bisa submit pharse 'success' ke server. Di level ini juga seluruh kode JavaScript bisa dilihat langsung di dalam halaman HTML, jadi kode dapat dibaca dan dianalisis secara langsung melalui fitur "View Page Source" browser.

![gambar_di_js_attack](assets/image/2026-02-14-javascript-attack/image1.png)

```javascript
/* MD5 code from: https://github.com/blueimp/JavaScript-MD5 */
// [MD5 library code – digunakan untuk hashing]

function rot13(inp) {
    return inp.replace(/[a-zA-Z]/g, function(c) {
        return String.fromCharCode(
            (c <= 'Z' ? 90 : 122) >= (c = c.charCodeAt(0) + 13) ? c : c - 26 ....
        );
    });
}

function generate_token() {
    var phrase = document.getElementById('phrase').value;
    document.getElementById('token').value = md5(rot13(phrase));
}

generate_token();  // Dipanggil otomatis saat halaman dimuat
```

bisa dilihat dari kode diatas ada 2 function utama yang terekspos, yaitu function `rot13` untuk melakukan enkripsi dari inputan form dan function `generate_token` untuk mebuat token dari hasil enkripsi funtion `rot13` yang kemudian di-hash menggunakan md5.

Jika kita langsung mengirim pharse `success` ke server itu tidak bisa, karena akan muncul 'invalid token' di form.

![gambar_di_js_attack](assets/image/2026-02-14-javascript-attack/image2.png)

Jadi disini kita diminta untuk memasukan token hasil generate funtion tadi. Untuk itu yang pertama bisa kita lakukan adalah dengan mengubah nilai pada input form **"Change your pharse"** menjadi `success`. Lalu kita buka console di browser, lalu masukan perintah berikut untuk memanggil fungsi pembuat token secara manual

```javascript
document.getElmentbyId('token').value   // <--meilhat token saat ini
generate_token();                       // <-- membuat token dan memasukannya ke dalam variabel token
document.getElmentbyId('token').value   //<-- melihat hasil perubahan token
```

![gambar_di_js_attack](assets/image/2026-02-14-javascript-attack/image3.png)

jika sudah berubah, klik tombol **"Submit"**. Halaman akan menampilkan pesan "Congratulations" yang menandakan Anda berhasil.

![gambar_di_js_attack](assets/image/2026-02-14-javascript-attack/image4.png)


### **Level Medium**

Pada level Medium, kode JavaScript telah dipisahkan ke dalam file eksternal tersendiri (.js)

![gambar_di_js_attack](assets/image/2026-02-14-javascript-attack/image5.png)

dan untuk isi file javascriptnya sendiri adalah seperti berikut

```javascript
function do_something(e) {
    for (var t = "", n = e.length - 1; n >= 0; n--)
        t += e[n];
    return t
}

setTimeout(function() {
    do_elsesomething("XX")
}, 300);

function do_elsesomething(e) {
    document.getElementById("token").value = do_something(e + document.getElementById("phrase").value + "XX")
}
```
![gambar_di_js_attack](assets/image/2026-02-14-javascript-attack/image6.png)

fungsi `do_elsesomething()` membuat token dengan format `reverse("XX" + phrase + "XX")`. Sehingga untuk phrase="success": token = `reverse("XX" + "success" + "XX") = "XXsseccusXX".`

Selanjutnya di Console browser, ubah nilai phrase menjadi 'success' dan panggil do_elsesomething() secara manual.

```javascript

document.getElementById('phrase').value = 'success';
do_elsesomething('XX');

// Verifikasi:
console.log(document.getElementById('token').value);

```

![gambar_di_js_attack](assets/image/2026-02-14-javascript-attack/image7.png)

Terakhir Submit form. Server memvalidasi token dan menampilkan pesan sukses.

![gambar_di_js_attack](assets/image/2026-02-14-javascript-attack/image8.png)
 

### **Level High**

Level High menggunakan obfuskasi JavaScript, sebuah teknik yang mengubah kode menjadi bentuk yang sangat sulit dibaca tanpa mengubah fungsionalitasnya. Pada level ini, dua lapisan obfuskasi telah diterapkan menggunakan Dan's Tools Packer dan JavaScript Obfuscator Tool. Meskipun sangat sulit dibaca secara manual, kode masih dapat dipulihkan menggunakan tools deobfuskasi.

```javascript

var a = ['fromCharCode', 'toString', 'replace', 'BeJ', '\x5cw+', 'Lyg', 'SuR', '(w(){\x273M\x203L\x27;q\x201l=\x273K\x203I\x203J\x20T\x27;q\x201R=1c\x202I===\x271n\x27;q\x20Y=1R?2I:{};p(Y.3N){1R=1O}q\x202L=!1R&&1c\x202M===\x271n\x27;q\x202o=!Y.2S&&1c\x202d===\x271n\x27&&2d.2Q&&2d.2Q.3S;p(2o){Y=3R}z\x20p(2L){Y=2M}q\x202G=!Y.3Q&&1c\x202g===\x271n\x27&&2g.X;q\x202s=1c\x202l===\x27w\x27&&2l.3P;q\x201y=!Y.3H&&1c\x20Z!==\x272T\x27;q\x20m=\x273G\x27.3z(\x27\x27);q\x202w=[-3y,3x,3v,3w];q\x20U=[24,16,8,0];q\x20K=[3A,3B,3F,3E,3D,3C,3T,3U,4d,4c,4b,49, ... ]

(function(c, d) {
    var e = function(f) {
        while (--f) {
            c['push'](c['shift']());
        }
    };
    e(++d);
}(a, 0x1f4));

var b = function(c, d) {
    c = c - 0x0;
    var e = a[c];
    return e;
};

eval(function(d, e, f, g, h, i) {
    h = function(j) {
        return (j < e ? '' : h(parseInt(j / e))) + ((j = j % e) > 0x23 ? String[b('0x0')](j + 0x1d) : j[b('0x1')](0x24));
    }
    ;
    if (!''[b('0x2')](/^/, String)) {
        while (f--) {
            i[h(f)] = g[f] || h(f);
        }
        g = [function(k) {
            if ('wpA' !== b('0x3')) {
                return i[k];
            } else {
                while (f--) {
                    i[k(f)] = g[f] || k(f);
                }
                g = [function(l) {
                    return i[l];
                }
                ];
                k = function() {
                    return b('0x4');
                }
                ;
                f = 0x1;
            }
        }
        ];
        h = function() {
            return b('0x4');
        }
        ;
        f = 0x1;
    }
    ;while (f--) {
        if (g[f]) {
            if (b('0x5') === b('0x6')) {
                return i[h];
            } else {
                d = d[b('0x2')](new RegExp('\x5cb' + h(f) + '\x5cb','g'), g[f]);
            }
        }
    }
    return d;
}(b('0x7'), 0x3e, 0x137, b('0x8')[b('0x9')]('|'), 0x0, {}));
```
```javascript


```


## **5. Kesimpulan**

Modul **JavaScript Attacks** di DVWA mengajarkan kita sebuah prinsip keamanan yang sangat penting:

> **Keamanan tidak boleh bergantung pada kerahasiaan kode client-side (Security by Obscurity).**

*   **Low**: Menunjukkan bahwa jika logika ada di client, kita bisa langsung menggunakannya.
*   **Medium**: Menunjukkan bahwa memisahkan dan meminifikasi kode tidak menghentikan penyerang yang gigih.
*   **High**: Menunjukkan bahwa meskipun kode diobfusaksi, pada akhirnya ia harus dieksekusi oleh browser, sehingga ia bisa dianalisis dan dimanipulasi. Kode yang sangat terobfuskasi hanya memperlambat, tidak menghentikan, penyerang.

Untuk mengamankan aplikasi, logika sensitif seperti validasi dan pembuatan token harus dilakukan di **server-side (back-end)**, di mana pengguna tidak bisa memanipulasinya. Kode JavaScript hanya boleh digunakan untuk meningkatkan pengalaman pengguna, bukan untuk mengamankan data.