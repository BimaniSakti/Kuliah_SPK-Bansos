import numpy as np
import json
import os

_BOBOT_PATH = os.path.join(os.path.dirname(__file__), 'config_bobot.json')

def calculate_ahp(matrix):
    """
    Menghitung bobot prioritas dan Consistency Ratio (CR) menggunakan metode AHP.
    
    :param matrix: List 2D (Matriks Perbandingan Berpasangan inputan Admin)
    :return: dict berisi array bobot, nilai CR, dan status kelolosan konsistensi
    """
    # Mengubah list Python biasa menjadi array NumPy untuk manipulasi matriks
    mat = np.array(matrix, dtype=float)
    n = mat.shape[0] # Mendapatkan ordo matriks (jumlah kriteria)
    
    # ==========================================
    # 1. NORMALISASI MATRIKS & MENGHITUNG BOBOT
    # ==========================================
    # Menjumlahkan nilai di setiap kolom
    col_sum = mat.sum(axis=0)
    
    # Normalisasi: membagi tiap elemen matriks dengan jumlah kolomnya
    normalized_mat = mat / col_sum
    
    # Bobot (Eigenvector): nilai rata-rata dari setiap baris pada matriks ternormalisasi
    weights = normalized_mat.mean(axis=1)
    
    # ==========================================
    # 2. UJI KONSISTENSI (CONSISTENCY RATIO)
    # ==========================================
    # Perkalian dot (titik) antara matriks asli dengan vektor bobot
    weighted_sum = np.dot(mat, weights)
    
    # Mencari nilai eigen maksimum (Lambda Max)
    lambda_max = np.mean(weighted_sum / weights)
    
    # Menghitung Consistency Index (CI)
    # Rumus: CI = (Lambda Max - n) / (n - 1)
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0
    
    # Daftar Random Index (RI) berdasarkan ketetapan standar Saaty
    # Index 1-10 secara berurutan
    ri_dict = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 
               6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    
    # Mengambil nilai RI sesuai jumlah kriteria (default 1.49 jika >10)
    ri = ri_dict.get(n, 1.49)
    
    # Menghitung Consistency Ratio (CR)
    cr = ci / ri if ri > 0 else 0
    
    # Syarat mutlak AHP: CR harus kurang dari atau sama dengan 10% (0.1)
    is_consistent = cr <= 0.1
    
    return {
        "weights": weights.tolist(), # Convert kembali ke list Python agar bisa dibaca JSON/Jinja
        "consistency_ratio": round(cr, 4), # Dibulatkan 4 angka di belakang koma
        "is_consistent": is_consistent
    }
    
def save_weights(ahp_weights):
    """Menyimpan 3 bobot pertama hasil AHP ke file JSON"""
    data = {"ahp_weights": ahp_weights}
    with open(_BOBOT_PATH, 'w') as f:
        json.dump(data, f)

def load_weights():
    """
    Membaca bobot AHP, lalu menggabungkannya dengan 6 kriteria statis lainnya
    agar totalnya menjadi 9 kriteria (total bobot 1.0) untuk mesin SAW.
    """
    # 6 Kriteria sisa (IPM, Harapan_Hidup, Sanitasi, Air, TPT, TPAK)
    # Total bobot sisa ini adalah 0.55
    static_weights = [0.15, 0.10, 0.05, 0.05, 0.15, 0.05]
    
    try:
        with open(_BOBOT_PATH, 'r') as f:
            data = json.load(f)
            ahp_w = data['ahp_weights']
            # Karena bobot sisa adalah 0.55, maka jatah 3 bobot pertama adalah 0.45 (1.0 - 0.55)
            # Kita kalikan hasil AHP (yang totalnya 1.0) dengan 0.45 agar proporsional
            adjusted_ahp = [w * 0.45 for w in ahp_w]
            return adjusted_ahp + static_weights
    except Exception:
        pass
        
    # Jika belum ada file konfigurasi yang disave Admin, gunakan default ini
    return [0.25, 0.10, 0.10] + static_weights

# ==========================================
# FUNGSI TESTING (Bisa dijalankan terpisah)
# ==========================================
if __name__ == '__main__':
    # Contoh matriks 4x4 (Misal: P0, Lama_Sekolah, Pengeluaran, TPT)
    contoh_matriks_admin = [
        [1,   5,   5,   9],
        [1/5, 1,   1,   3],
        [1/5, 1,   1,   3],
        [1/9, 1/3, 1/3, 1]
    ]
    
    hasil = calculate_ahp(contoh_matriks_admin)
    print("Bobot Kriteria:", hasil['weights'])
    print("Nilai CR:", hasil['consistency_ratio'])
    print("Data Konsisten?:", hasil['is_consistent'])