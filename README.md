# Watermarking Citra Digital - Sistem Multimedia

## Deskripsi
Program ini mengimplementasikan *invisible watermarking* pada citra digital menggunakan metode DCT (*Discrete Cosine Transform*). Watermark berupa deretan bit acak yang disisipkan secara tak kasat mata ke dalam gambar. Ketahanan watermark kemudian dievaluasi terhadap kompresi JPEG dengan berbagai nilai *Quality Factor* (QF).

## Algoritma yang Digunakan
- **DCT (Discrete Cosine Transform)** : mengubah blok pixel ke domain frekuensi sehingga watermark dapat disisipkan ke koefisien frekuensi menengah
- **YCrCb Color Space** : gambar dikonversi ke ruang warna YCrCb agar watermark hanya disisipkan ke channel Y (luminance/kecerahan), sehingga warna gambar tidak berubah

## Proses Watermarking

### 1. Load Gambar
Gambar wajah dibaca dalam format berwarna (BGR) menggunakan OpenCV.

### 2. Konversi ke YCrCb
Gambar dikonversi dari format BGR ke YCrCb. Ruang warna ini memisahkan informasi kecerahan (channel Y) dari informasi warna (channel Cr dan Cb). Watermark hanya disisipkan ke channel Y agar warna gambar tetap tidak berubah secara visual.

### 3. Pembuatan Watermark Acak
Watermark dibuat berupa array acak berisi nilai 0 dan 1 sebanyak jumlah blok 8x8 pixel yang ada di gambar. Nilai seed (seed=42) digunakan agar watermark yang dihasilkan selalu sama setiap kali program dijalankan.

### 4. Penyisipan Watermark (Embed)
Channel Y dibagi menjadi blok-blok berukuran 8x8 pixel. Setiap blok kemudian diproses sebagai berikut:
- Blok di-transformasi menggunakan DCT sehingga menghasilkan koefisien-koefisien frekuensi
- Bit watermark disisipkan ke 3 koefisien frekuensi menengah dengan menambahkan nilai alpha (kekuatan watermark)
- Blok dikembalikan ke domain spasial menggunakan Inverse DCT

Setelah semua blok diproses, channel Y yang telah mengandung watermark digabungkan kembali dengan channel Cr dan Cb, lalu dikonversi balik ke format BGR. Hasilnya adalah gambar berwarna yang telah mengandung watermark secara invisible.

### 5. Kompresi JPEG
Gambar yang telah di-watermark dikompres menggunakan kompresi JPEG dengan 5 nilai Quality Factor yang berbeda, yaitu QF = 10, 30, 50, 70, dan 90. Semakin kecil nilai QF, semakin besar tingkat kompresi dan semakin banyak detail gambar yang hilang.

### 6. Ekstraksi Watermark
Dari setiap gambar yang telah dikompres, channel Y-nya dibaca dan dibandingkan dengan channel Y gambar asli menggunakan DCT. Selisih koefisien frekuensi antara keduanya merepresentasikan watermark yang berhasil diekstrak.

### 7. Evaluasi
Watermark hasil ekstraksi dibandingkan dengan watermark asli menggunakan nilai korelasi. Nilai korelasi berkisar antara -1 hingga 1. Jika nilai korelasi lebih dari 0.3, watermark dinyatakan masih dapat terbaca. Jika di bawah 0.3, watermark dinyatakan tidak dapat diekstrak akibat kerusakan yang disebabkan oleh kompresi.

## Requirements
```
pip install numpy opencv-python scipy matplotlib
```

## Cara Menjalankan
1. Letakkan file foto di folder yang sama dengan `main.py`
2. Sesuaikan nama file foto di `main.py` pada variabel `IMAGE_PATH`
3. Jalankan program:
```
python main.py
```
4. Hasil evaluasi akan tersimpan di folder `output/`

## Output
- Grafik korelasi watermark terhadap nilai Quality Factor (QF)
- Gambar original, gambar setelah watermark, dan gambar hasil kompresi pada setiap QF
- Status watermark terbaca/tidak terbaca pada terminal
