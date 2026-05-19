import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from watermark import (
    load_image,
    generate_watermark,
    embed_watermark,
    extract_watermark,
    evaluate_watermark
)

# =====================
# KONFIGURASI
# =====================
IMAGE_PATH = "foto watermarking.jpeg"
ALPHA = 50
QF_LIST = [10, 30, 50, 70, 90]
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================
# 1. LOAD GAMBAR
# =====================
print("Loading gambar...")
image = load_image(IMAGE_PATH)
h, w = image.shape[:2]
h8 = (h // 8) * 8
w8 = (w // 8) * 8
n_blocks = (h8 // 8) * (w8 // 8)
print(f"Ukuran gambar: {image.shape} | Jumlah blok 8x8: {n_blocks}")

# Gambar 1 — Original
fig, ax = plt.subplots(figsize=(6, 5))
ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
ax.set_title('Gambar Original')
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "1_original.png"), dpi=150)
plt.close()
print("Gambar 1 (original) disimpan!")

# =====================
# 2. KONVERSI YCrCb
# =====================
ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
Y_original = ycrcb[:, :, 0]
Cr_original = ycrcb[:, :, 1]
Cb_original = ycrcb[:, :, 2]

# Gambar 2 — Channel YCrCb
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Konversi YCrCb', fontsize=14, fontweight='bold')
axes[0].imshow(Y_original, cmap='gray')
axes[0].set_title('Channel Y (Luminance)')
axes[0].axis('off')
axes[1].imshow(Cr_original, cmap='Reds')
axes[1].set_title('Channel Cr (Warna Merah)')
axes[1].axis('off')
axes[2].imshow(Cb_original, cmap='Blues')
axes[2].set_title('Channel Cb (Warna Biru)')
axes[2].axis('off')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "2_konversi_ycrcb.png"), dpi=150)
plt.close()
print("Gambar 2 (konversi YCrCb) disimpan!")

# =====================
# 3. PEMBUATAN WATERMARK
# =====================
print("Membuat watermark acak...")
watermark = generate_watermark(n_blocks, h8=h8, w8=w8)
wm_visual = watermark.reshape(h8 // 8, w8 // 8)

# Gambar 3 — Watermark
fig, ax = plt.subplots(figsize=(6, 5))
ax.imshow(wm_visual, cmap='gray')
ax.set_title('Watermark Acak (Random Noise)')
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "3_watermark.png"), dpi=150)
plt.close()
print("Gambar 3 (watermark) disimpan!")

# =====================
# 4. PENYISIPAN WATERMARK
# =====================
print("Meng-embed watermark ke gambar...")
watermarked_image = embed_watermark(image, watermark, alpha=ALPHA)
diff = cv2.absdiff(image, watermarked_image)
diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
diff_enhanced = cv2.equalizeHist(diff_gray)

cv2.imwrite(os.path.join(OUTPUT_DIR, "original.png"), image)
cv2.imwrite(os.path.join(OUTPUT_DIR, "watermarked.png"), watermarked_image)

# Gambar 4 — Penyisipan watermark
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Penyisipan Watermark', fontsize=14, fontweight='bold')
axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
axes[0].set_title('Sebelum Watermark')
axes[0].axis('off')
axes[1].imshow(cv2.cvtColor(watermarked_image, cv2.COLOR_BGR2RGB))
axes[1].set_title('Setelah Watermark')
axes[1].axis('off')
axes[2].imshow(diff_enhanced, cmap='hot')
axes[2].set_title('Selisih (diperbesar 10x)')
axes[2].axis('off')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "4_penyisipan_watermark.png"), dpi=150)
plt.close()
print("Gambar 4 (penyisipan watermark) disimpan!")

# =====================
# 5. KOMPRESI JPEG & EVALUASI
# =====================
print("\n=== Evaluasi per Quality Factor ===")
correlations = []
extracted_wms = []

for qf in QF_LIST:
    compressed_path = os.path.join(OUTPUT_DIR, f"compressed_qf{qf}.jpg")
    cv2.imwrite(compressed_path, watermarked_image, [cv2.IMWRITE_JPEG_QUALITY, qf])
    extracted = extract_watermark(Y_original, compressed_path, alpha=ALPHA)
    corr = evaluate_watermark(watermark, extracted)
    correlations.append(corr)
    extracted_wms.append(extracted)
    status = "✓ TERBACA" if corr > 0.3 else "✗ TIDAK TERBACA"
    print(f"QF = {qf:3d} | Korelasi = {corr:.4f} | {status}")

# Gambar 5 — Kompresi JPEG
fig, axes = plt.subplots(1, len(QF_LIST), figsize=(18, 5))
fig.suptitle('Hasil Kompresi JPEG per Quality Factor', fontsize=14, fontweight='bold')
for i, qf in enumerate(QF_LIST):
    compressed_path = os.path.join(OUTPUT_DIR, f"compressed_qf{qf}.jpg")
    img_comp = cv2.imread(compressed_path)
    axes[i].imshow(cv2.cvtColor(img_comp, cv2.COLOR_BGR2RGB))
    axes[i].set_title(f'QF = {qf}')
    axes[i].axis('off')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "5_kompresi_jpeg.png"), dpi=150)
plt.close()
print("Gambar 5 (kompresi JPEG) disimpan!")

# Gambar 6 — Ekstraksi watermark
fig, axes = plt.subplots(1, len(QF_LIST), figsize=(18, 5))
fig.suptitle('Watermark yang Diekstrak per Quality Factor', fontsize=14, fontweight='bold')
for i, qf in enumerate(QF_LIST):
    extr = extracted_wms[i]
    extr_visual = extr.reshape(h8 // 8, w8 // 8)
    axes[i].imshow(extr_visual, cmap='gray')
    status = "✓ TERBACA" if correlations[i] > 0.3 else "✗ TIDAK TERBACA"
    axes[i].set_title(f'QF = {qf}\nKorelasi: {correlations[i]:.3f}\n{status}',
                      color='green' if correlations[i] > 0.3 else 'red')
    axes[i].axis('off')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "6_ekstraksi_watermark.png"), dpi=150)
plt.close()
print("Gambar 6 (ekstraksi watermark) disimpan!")

# Gambar 7 — Grafik korelasi
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(QF_LIST, correlations, 'bo-', linewidth=2, markersize=8)
ax.axhline(y=0.3, color='r', linestyle='--', label='Threshold (0.3)')
for qf, corr in zip(QF_LIST, correlations):
    ax.annotate(f'{corr:.3f}', (qf, corr), textcoords="offset points", xytext=(0, 10), ha='center')
ax.set_xlabel('Quality Factor (QF)')
ax.set_ylabel('Korelasi')
ax.set_title('Ketahanan Watermark terhadap Kompresi JPEG')
ax.legend()
ax.grid(True)
ax.set_xticks(QF_LIST)
ax.set_ylim(-0.1, 1.1)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "7_grafik_korelasi.png"), dpi=150)
plt.close()
print("Gambar 7 (grafik korelasi) disimpan!")

print("\nSemua hasil evaluasi disimpan di folder output!")