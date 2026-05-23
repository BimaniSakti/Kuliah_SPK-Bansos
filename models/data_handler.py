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

def hapus_wilayah(kab_kota):
    engine = get_engine()
    with engine.connect() as conn:
        # Perintah SQL untuk menghapus data berdasarkan nama Kab/Kota
        query = text("DELETE FROM data_wilayah WHERE `Kab/Kota` = :kab_kota")
        conn.execute(query, {"kab_kota": kab_kota})
        conn.commit()
        
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