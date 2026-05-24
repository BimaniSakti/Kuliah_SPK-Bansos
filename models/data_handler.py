import pandas as pd
from sqlalchemy import create_engine, text

def get_engine():
    # Fungsi bantuan agar tidak perlu menulis ulang koneksi database
    return create_engine('mysql+pymysql://root:@localhost/spk_bansos_jabar')

def load_data():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM data_wilayah", con=engine)
    return df

def tambah_wilayah(data):
    engine = get_engine()
    with engine.connect() as conn:
        # Perintah SQL untuk memasukkan baris data baru
        query = text("""
            INSERT INTO data_wilayah 
            (Provinsi, `Kab/Kota`, P0, Lama_Sekolah, Pengeluaran, IPM, Harapan_Hidup, Sanitasi, Air_Minum, TPT, TPAK, PDRB, Klasifikasi_Awal) 
            VALUES (:provinsi, :kab_kota, :p0, :lama_sekolah, :pengeluaran, :ipm, :harapan_hidup, :sanitasi, :air_minum, :tpt, :tpak, 0, 0)
        """)
        conn.execute(query, data)
        conn.commit()
        
def edit_wilayah(data):
    """Fungsi untuk memperbarui data wilayah yang sudah ada"""
    engine = get_engine()
    with engine.connect() as conn:
        query = text("""
            UPDATE data_wilayah 
            SET Provinsi=:provinsi, P0=:p0, Lama_Sekolah=:lama_sekolah, 
                Pengeluaran=:pengeluaran, IPM=:ipm, Harapan_Hidup=:harapan_hidup, 
                Sanitasi=:sanitasi, Air_Minum=:air_minum, TPT=:tpt, TPAK=:tpak
            WHERE `Kab/Kota` = :kab_kota
        """)
        conn.execute(query, data)
        conn.commit()

def hapus_wilayah(kab_kota):
    engine = get_engine()
    with engine.connect() as conn:
        # Perintah SQL untuk menghapus data berdasarkan nama Kab/Kota
        query = text("DELETE FROM data_wilayah WHERE `Kab/Kota` = :kab_kota")
        conn.execute(query, {"kab_kota": kab_kota})
        conn.commit()

def import_csv_ke_db(file_obj):
    """Fungsi untuk mereplace seluruh tabel MySQL dengan file CSV baru"""
    engine = get_engine()
    df = pd.read_csv(file_obj)
    
    # Samakan format kolomnya
    df.rename(columns={
        'Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)': 'P0',
        'Rata-rata Lama Sekolah Penduduk 15+ (Tahun)': 'Lama_Sekolah',
        'Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)': 'Pengeluaran',
        'Indeks Pembangunan Manusia': 'IPM',
        'Umur Harapan Hidup (Tahun)': 'Harapan_Hidup',
        'Persentase rumah tangga yang memiliki akses terhadap sanitasi layak': 'Sanitasi',
        'Persentase rumah tangga yang memiliki akses terhadap air minum layak': 'Air_Minum',
        'Tingkat Pengangguran Terbuka': 'TPT',
        'Tingkat Partisipasi Angkatan Kerja': 'TPAK',
        'PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)': 'PDRB',
        'Klasifikasi Kemiskinan': 'Klasifikasi_Awal'
    }, inplace=True)
    
    df.fillna(0, inplace=True)
    df.to_sql(name='data_wilayah', con=engine, if_exists='replace', index=False)
        
def simpan_hasil_model(df_hasil):
    """Menyimpan Skor SAW dan Kategori Prioritas ke database MySQL"""
    engine = get_engine()
    with engine.connect() as conn:
        # Trik aman: Mencoba membuat kolom baru. Jika error (karena kolom sudah ada), abaikan.
        try:
            conn.execute(text("ALTER TABLE data_wilayah ADD COLUMN Skor_SAW FLOAT DEFAULT 0"))
            conn.execute(text("ALTER TABLE data_wilayah ADD COLUMN Kategori_Prioritas VARCHAR(50) DEFAULT 'Belum Dihitung'"))
        except:
            pass 
        
        # Mengupdate skor dan label untuk setiap wilayah
        for _, row in df_hasil.iterrows():
            query = text("""
                UPDATE data_wilayah 
                SET Skor_SAW = :skor, Kategori_Prioritas = :kategori
                WHERE `Kab/Kota` = :kab_kota
            """)
            conn.execute(query, {
                "skor": row.get('Skor_SAW', 0), 
                "kategori": row.get('Kategori_Prioritas', 'Menunggu Model'),
                "kab_kota": row['Kab/Kota']
            })
        conn.commit()