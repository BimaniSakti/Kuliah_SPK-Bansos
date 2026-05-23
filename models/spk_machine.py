import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def calculate_saw(df, criteria_cols, weights, types):
    """
    Melakukan normalisasi matriks dan perhitungan preferensi akhir menggunakan metode SAW.
    
    :param df: DataFrame pandas berisi data mentah
    :param criteria_cols: List nama kolom kriteria yang dihitung
    :param weights: Array/List bobot dari hasil AHP
    :param types: List tipe kriteria ('benefit' atau 'cost')
    :return: DataFrame yang sudah memiliki kolom 'Skor_SAW'
    """
    df_result = df.copy()
    
    # Membuat DataFrame kosong untuk menyimpan matriks normalisasi
    norm_matrix = pd.DataFrame(index=df.index, columns=criteria_cols)
    
    for i, col in enumerate(criteria_cols):
        # Mengubah data kolom menjadi float untuk menghindari error kalkulasi
        col_data = df_result[col].astype(float)
        
        if types[i] == 'benefit':
            # Rumus Benefit: Nilai / Nilai Maksimum
            max_val = col_data.max()
            norm_matrix[col] = np.where(max_val == 0, 0, col_data / max_val)
        else:
            # Rumus Cost: Nilai Minimum / Nilai
            min_val = col_data.min()
            norm_matrix[col] = np.where(col_data == 0, 0, min_val / col_data)
            
    # Mengalikan matriks normalisasi dengan bobot, lalu jumlahkan ke samping (axis=1)
    df_result['Skor_SAW'] = (norm_matrix * weights).sum(axis=1)
    
    # Membulatkan skor menjadi 4 angka di belakang koma untuk estetika UI
    df_result['Skor_SAW'] = df_result['Skor_SAW'].round(4)
    
    return df_result

def apply_kmeans(df, num_clusters=3):
    """
    Melatih model K-Means menggunakan Skor SAW untuk menentukan label prioritas wilayah.
    
    :param df: DataFrame yang sudah memiliki kolom 'Skor_SAW'
    :param num_clusters: Jumlah klaster target (default = 3: Tinggi, Sedang, Rendah)
    :return: Tuple (DataFrame berlabel, Nilai Silhouette Score)
    """
    df_result = df.copy()
    
    # Scikit-Learn membutuhkan array 2D, jadi kita reshape skor SAW-nya
    X = df_result[['Skor_SAW']].values
    
    # Inisialisasi model K-Means (n_init=10 agar hasil stabil dan konsisten)
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    
    # Mengukur seberapa akurat pemisahan klasternya
    sil_score = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else 0
    
    # Mapping Label Prioritas Secara Otomatis
    # Kita tidak tahu klaster 0, 1, 2 itu posisinya di mana, jadi kita urutkan centroidnya
    centroids = kmeans.cluster_centers_.flatten()
    sorted_indices = np.argsort(centroids)
    
    # Nilai terkecil = Prioritas Rendah, Tengah = Sedang, Terbesar = Tinggi
    label_map = {
        sorted_indices[0]: "Prioritas Rendah",
        sorted_indices[1]: "Prioritas Sedang",
        sorted_indices[2]: "Prioritas Tinggi"
    }
    
    # Terapkan label ke dalam DataFrame
    df_result['Kategori_Prioritas'] = [label_map[label] for label in labels]
    
    return df_result, round(sil_score, 3)