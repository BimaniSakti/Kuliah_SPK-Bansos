import pandas as pd
from sqlalchemy import create_engine

print("Membaca file CSV...")
df = pd.read_csv('Klasifikasi Tingkat Kemiskinan pada Indonesia.csv')

# Merapikan nama kolom persis seperti sebelumnya sebelum dimasukkan ke database
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

print("Menyambungkan ke MySQL Laragon...")
# Format: mysql+pymysql://username:password@host/nama_database
engine = create_engine('mysql+pymysql://root:@localhost/spk_bansos_jabar')

print("Mentransfer data ke tabel 'data_wilayah'...")
# Perintah ajaib ini akan otomatis membuat tabel dan mengisi datanya!
df.to_sql(name='data_wilayah', con=engine, if_exists='replace', index=False)