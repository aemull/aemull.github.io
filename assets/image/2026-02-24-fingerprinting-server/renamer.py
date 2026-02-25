"""
Image Auto-Renamer
==================
Otomatis mengubah nama file gambar di suatu direktori menjadi image_1, image_2, dst.

Aturan:
- File lama yang sudah bernama image_N TIDAK akan direname ulang.
- File baru (belum bernama image_N) akan mengisi celah nomor yang kosong terlebih dahulu,
  baru kemudian melanjutkan ke nomor berikutnya setelah yang terbesar.
- Saat file dihapus, celah nomornya dibiarkan kosong hingga ada file baru yang mengisinya.

Cara pakai:
    pip install watchdog
    python image_renamer.py /path/ke/direktori

Jika tidak ada argumen, akan memantau direktori saat ini.
"""

import os
import sys
import time
import re
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif', '.heic', '.svg'}
NAMED_PATTERN = re.compile(r'^image_(\d+)\.[a-zA-Z]+$')


def is_image(filename: str) -> bool:
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS


def get_used_numbers(directory: str) -> set:
    """Ambil semua nomor yang sudah dipakai oleh file image_N."""
    numbers = set()
    for f in os.listdir(directory):
        match = NAMED_PATTERN.match(f)
        if match:
            numbers.add(int(match.group(1)))
    return numbers


def get_gaps_then_next(used_numbers: set) -> list:
    """
    Kembalikan daftar nomor yang tersedia untuk dipakai:
    celah yang kosong (urut dari kecil) + nomor baru setelah yang terbesar.
    """
    if not used_numbers:
        # Belum ada file, mulai dari 1
        return list(range(1, 1000))  # generator cukup banyak
    max_num = max(used_numbers)
    available = []
    # Isi celah dulu
    for n in range(1, max_num + 1):
        if n not in used_numbers:
            available.append(n)
    # Lanjut ke nomor baru
    available.append(max_num + 1)
    return available


def rename_file_safely(src: str, dst: str) -> bool:
    """Rename file, hindari konflik nama."""
    if src == dst:
        return True
    if os.path.exists(dst):
        print(f"  ⚠ Lewati (nama sudah ada): {os.path.basename(dst)}")
        return False
    try:
        os.rename(src, dst)
        print(f"  ✔ {os.path.basename(src)}  →  {os.path.basename(dst)}")
        return True
    except Exception as e:
        print(f"  ✘ Gagal rename {os.path.basename(src)}: {e}")
        return False


def process_new_files(directory: str):
    """
    Hanya rename file yang BELUM bernama image_N.
    File lama (image_N) sama sekali tidak disentuh.
    Celah nomor diisi oleh file baru terlebih dahulu.
    """
    all_files = [
        f for f in os.listdir(directory)
        if is_image(f) and os.path.isfile(os.path.join(directory, f))
    ]

    unnamed = sorted([f for f in all_files if not NAMED_PATTERN.match(f)])

    if not unnamed:
        return  # Tidak ada file baru, tidak ada yang perlu dilakukan

    used_numbers = get_used_numbers(directory)
    available = get_gaps_then_next(used_numbers)
    avail_iter = iter(available)

    for fname in unnamed:
        ext = Path(fname).suffix.lower()
        try:
            num = next(avail_iter)
            # Pastikan nomornya belum dipakai (karena list available mungkin terbatas)
            while num in used_numbers:
                num = next(avail_iter)
        except StopIteration:
            print("  ✘ Tidak ada nomor tersedia (tidak seharusnya terjadi).")
            break

        new_name = f"image_{num}{ext}"
        src = os.path.join(directory, fname)
        dst = os.path.join(directory, new_name)
        if rename_file_safely(src, dst):
            used_numbers.add(num)


class ImageRenameHandler(FileSystemEventHandler):
    def __init__(self, directory: str):
        self.directory = directory
        self._lock = threading.Lock()
        self._debounce_timer = None

    def _schedule_process(self, delay=1.0):
        """Tunda proses sedikit agar file selesai di-copy dulu."""
        with self._lock:
            if self._debounce_timer:
                self._debounce_timer.cancel()
            self._debounce_timer = threading.Timer(delay, self._do_process)
            self._debounce_timer.start()

    def _do_process(self):
        with self._lock:
            self._debounce_timer = None
        process_new_files(self.directory)

    def on_created(self, event):
        if not event.is_directory and is_image(event.src_path):
            fname = os.path.basename(event.src_path)
            print(f"\n📥 File baru terdeteksi: {fname}")
            self._schedule_process(delay=1.0)

    def on_deleted(self, event):
        if not event.is_directory and is_image(event.src_path):
            fname = os.path.basename(event.src_path)
            print(f"\n🗑️  File dihapus: {fname}  (celah nomor dibiarkan, menunggu file baru)")

    def on_moved(self, event):
        if not event.is_directory:
            dest_is_image = is_image(event.dest_path)
            src_is_image = is_image(event.src_path)
            if dest_is_image and not NAMED_PATTERN.match(os.path.basename(event.dest_path)):
                fname = os.path.basename(event.dest_path)
                print(f"\n📋 File dipindahkan ke direktori: {fname}")
                self._schedule_process(delay=1.0)
            elif src_is_image and not dest_is_image:
                fname = os.path.basename(event.src_path)
                print(f"\n🗑️  File dipindahkan keluar: {fname}  (celah nomor dibiarkan)")


def main():
    if len(sys.argv) > 1:
        watch_dir = sys.argv[1]
    else:
        watch_dir = os.getcwd()

    watch_dir = os.path.abspath(watch_dir)

    if not os.path.isdir(watch_dir):
        print(f"❌ Direktori tidak ditemukan: {watch_dir}")
        sys.exit(1)

    print(f"🖼️  Image Auto-Renamer aktif")
    print(f"📁 Memantau : {watch_dir}")
    print(f"   Format   : image_1, image_2, image_3, ...")
    print(f"   File lama : TIDAK akan direname ulang")
    print(f"   Celah     : diisi oleh file BARU yang masuk")
    print(f"   Tekan Ctrl+C untuk berhenti\n")

    # Proses file tak bernama yang sudah ada saat program dijalankan
    process_new_files(watch_dir)

    observer = Observer()
    handler = ImageRenameHandler(watch_dir)
    observer.schedule(handler, watch_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Program dihentikan.")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()