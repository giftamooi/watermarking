import numpy as np
import cv2
from scipy.fftpack import dct, idct

def load_image(path):
    #Load gambar berwarna (BGR)
    img = cv2.imread(path)
    return img

def generate_watermark(n_blocks, seed=42):
    #Buat watermark acak sejumlah blok yang ada
    np.random.seed(seed)
    watermark = np.random.randint(0, 2, n_blocks).astype(np.float32)
    return watermark

def dct2(block):
    #DCT 2D
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

def idct2(block):
    #Inverse DCT 2D
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

def embed_watermark(image, watermark, alpha=50):
    #Embed watermark ke channel Y (luminance) gambar berwarna
    #Gambar tetap berwarna, watermark invisible
    # Convert BGR ke YCrCb
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    Y = ycrcb[:, :, 0].astype(np.float32)

    h, w = Y.shape
    h8 = (h // 8) * 8
    w8 = (w // 8) * 8
    Y = Y[:h8, :w8]
    Y_wm = Y.copy()

    idx = 0
    for i in range(0, h8, 8):
        for j in range(0, w8, 8):
            block = Y[i:i+8, j:j+8]
            dct_block = dct2(block)
            bit = 2 * watermark[idx % len(watermark)] - 1
            dct_block[2, 5] += alpha * bit
            dct_block[5, 2] += alpha * bit
            dct_block[3, 4] += alpha * bit
            Y_wm[i:i+8, j:j+8] = idct2(dct_block)
            idx += 1

    Y_wm = np.clip(Y_wm, 0, 255).astype(np.uint8)

    # Gabung balik ke YCrCb lalu convert ke BGR
    ycrcb_wm = ycrcb.copy()
    ycrcb_wm[:h8, :w8, 0] = Y_wm
    watermarked_bgr = cv2.cvtColor(ycrcb_wm, cv2.COLOR_YCrCb2BGR)
    return watermarked_bgr

def extract_watermark(original_gray, watermarked_path, alpha=50):
    #Ekstrak watermark dari gambar yang sudah dikompres
    #original_gray = channel Y dari gambar asli
    compressed = cv2.imread(watermarked_path)
    compressed_ycrcb = cv2.cvtColor(compressed, cv2.COLOR_BGR2YCrCb)
    compressed_Y = compressed_ycrcb[:, :, 0].astype(np.float32)

    orig = original_gray.astype(np.float32)
    h, w = orig.shape
    h8 = (h // 8) * 8
    w8 = (w // 8) * 8
    orig = orig[:h8, :w8]
    compressed_Y = compressed_Y[:h8, :w8]

    n_blocks = (h8 // 8) * (w8 // 8)
    extracted = np.zeros(n_blocks, dtype=np.float32)

    idx = 0
    for i in range(0, h8, 8):
        for j in range(0, w8, 8):
            dct_orig = dct2(orig[i:i+8, j:j+8])
            dct_comp = dct2(compressed_Y[i:i+8, j:j+8])
            diff = (
                (dct_comp[2, 5] - dct_orig[2, 5]) +
                (dct_comp[5, 2] - dct_orig[5, 2]) +
                (dct_comp[3, 4] - dct_orig[3, 4])
            ) / (3 * alpha)
            extracted[idx] = diff
            idx += 1

    return extracted

def evaluate_watermark(original_wm, extracted_wm):
    #Hitung korelasi antara watermark asli dan yang diekstrak
    #Makin tinggi = makin mirip = watermark masih terbaca
    orig = (2 * original_wm - 1).flatten()
    extr = extracted_wm.flatten()
    min_len = min(len(orig), len(extr))
    orig = orig[:min_len]
    extr = extr[:min_len]
    if np.std(extr) == 0:
        return 0.0
    correlation = np.corrcoef(orig, extr)[0, 1]
    return float(correlation)