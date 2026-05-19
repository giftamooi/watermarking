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
# 1. LOAD GAMBAR BERWARNA
# =====================
print("Loading gambar...")
image = load_image(IMAGE_PATH)
h, w = image.shape[:2]
h8 = (h // 8) * 8
w8 = (w // 8) * 8
n_blocks = (h8 // 8) * (w8 // 8)
print(f"Ukuran gambar: {image.shape} | Jumlah blok 8x8: {n_blocks}")

# Ambil channel Y untuk keperluan ekstraksi nanti
ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
Y_original = ycrcb[:, :, 0]

# =====================
# 2. BUAT WATERMARK ACAK
# =====================
print("Membuat watermark acak...")
watermark = generate_watermark(n_blocks, seed=42)
print(f"Jumlah bit watermark: {len(watermark)}")

# =====================
# 3. EMBED WATERMARK
# =====================
print("Meng-embed watermark ke gambar...")
watermarked_image = embed_watermark(image, watermark, alpha=ALPHA)

cv2.imwrite(os.path.join(OUTPUT_DIR, "original.png"), image)
cv2.imwrite(os.path.join(OUTPUT_DIR, "watermarked.png"), watermarked_image)
print("Gambar watermarked disimpan!\n")

# =====================
# 4. KOMPRES JPEG & EVALUASI
# =====================
print("=== Evaluasi per Quality Factor ===")
correlations = []

for qf in QF_LIST:
    compressed_path = os.path.join(OUTPUT_DIR, f"compressed_qf{qf}.jpg")
    cv2.imwrite(compressed_path, watermarked_image, [cv2.IMWRITE_JPEG_QUALITY, qf])

    extracted = extract_watermark(Y_original, compressed_path, alpha=ALPHA)
    corr = evaluate_watermark(watermark, extracted)
    correlations.append(corr)

    status = "✓ TERBACA" if corr > 0.3 else "✗ TIDAK TERBACA"
    print(f"QF = {qf:3d} | Korelasi = {corr:.4f} | {status}")

# =====================
# 5. PLOT HASIL
# =====================
plt.figure(figsize=(14, 10))

# Original berwarna
plt.subplot(2, 3, 1)
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.title('Original (Berwarna)')
plt.axis('off')

# Setelah watermark (berwarna)
plt.subplot(2, 3, 2)
plt.imshow(cv2.cvtColor(watermarked_image, cv2.COLOR_BGR2RGB))
plt.title('Setelah Watermark')
plt.axis('off')

# Watermark acak
wm_visual = watermark.reshape(h8 // 8, w8 // 8)
plt.subplot(2, 3, 3)
plt.imshow(wm_visual, cmap='gray')
plt.title('Watermark Acak (Asli)')
plt.axis('off')

# Compressed QF rendah
img_low = cv2.imread(os.path.join(OUTPUT_DIR, f"compressed_qf{QF_LIST[0]}.jpg"))
plt.subplot(2, 3, 4)
plt.imshow(cv2.cvtColor(img_low, cv2.COLOR_BGR2RGB))
plt.title(f'Compressed QF={QF_LIST[0]}')
plt.axis('off')

# Compressed QF tinggi
img_high = cv2.imread(os.path.join(OUTPUT_DIR, f"compressed_qf{QF_LIST[-1]}.jpg"))
plt.subplot(2, 3, 5)
plt.imshow(cv2.cvtColor(img_high, cv2.COLOR_BGR2RGB))
plt.title(f'Compressed QF={QF_LIST[-1]}')
plt.axis('off')

# Grafik korelasi vs QF
plt.subplot(2, 3, 6)
plt.plot(QF_LIST, correlations, 'bo-', linewidth=2, markersize=8)
plt.axhline(y=0.3, color='r', linestyle='--', label='Threshold (0.3)')
plt.xlabel('Quality Factor (QF)')
plt.ylabel('Korelasi')
plt.title('Ketahanan Watermark vs QF')
plt.legend()
plt.grid(True)
plt.xticks(QF_LIST)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "hasil_evaluasi.png"), dpi=150)
plt.show()
print("\nHasil evaluasi disimpan di folder output")