from flask import Flask, render_template, request, redirect, url_for
from models.data_handler import hapus_wilayah, load_data, simpan_hasil_model, tambah_wilayah
from models.spk_machine import calculate_saw, apply_kmeans 
from models.ahp_engine import calculate_ahp # Import fungsi kalkulator AHP


app = Flask(__name__)

# ==========================================
# ROUTING AREA PUBLIK
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    df = load_data()
    df_jabar = df[df['Provinsi'] == 'JAWA BARAT'].copy()
    
    total_jabar = len(df_jabar)
    total_nasional = len(df)
    tinggi = sedang = rendah = 0
    
    if 'Kategori_Prioritas' in df_jabar.columns:
        tinggi = len(df_jabar[df_jabar['Kategori_Prioritas'] == 'Prioritas Tinggi'])
        sedang = len(df_jabar[df_jabar['Kategori_Prioritas'] == 'Prioritas Sedang'])
        rendah = len(df_jabar[df_jabar['Kategori_Prioritas'] == 'Prioritas Rendah'])
        
    return render_template('dashboard.html', 
                           total_jabar=total_jabar, tinggi=tinggi, 
                           sedang=sedang, rendah=rendah, total_nasional=total_nasional)

@app.route('/ranking')
def ranking():
    df = load_data()
    df_jabar = df[df['Provinsi'] == 'JAWA BARAT'].copy()
    
    # Hanya urutkan jika kolom Skor_SAW sudah terbuat di DB (sudah dieksekusi admin)
    if 'Skor_SAW' in df_jabar.columns:
        df_jabar = df_jabar.sort_values(by='Skor_SAW', ascending=False)
        
    data_jabar = df_jabar.to_dict(orient='records')
    return render_template('ranking.html', data_wilayah=data_jabar)

# ==========================================
# ROUTING AREA ADMIN
# ==========================================
@app.route('/admin')
def admin_data():
    df = load_data()
    data_nasional = df.to_dict(orient='records')
    return render_template('admin_data.html', data_wilayah=data_nasional, total_data=len(data_nasional))

@app.route('/admin/ahp', methods=['GET', 'POST'])
def admin_ahp():
    ahp_result = None
    
    if request.method == 'POST':
        # Mengambil nilai skala Saaty dari form HTML, default ke 1 jika kosong
        p1 = float(request.form.get('pair1', 1)) # P0 vs Lama Sekolah
        p2 = float(request.form.get('pair2', 1)) # P0 vs Pengeluaran
        p3 = float(request.form.get('pair3', 1)) # Lama Sekolah vs Pengeluaran
        
        # Menyusun array Matriks 3x3 berdasarkan aturan kebalikan Saaty
        # Baris 1: 1, p1, p2
        # Baris 2: 1/p1, 1, p3
        # Baris 3: 1/p2, 1/p3, 1
        matrix = [
            [1.0, p1, p2],
            [1.0/p1, 1.0, p3],
            [1.0/p2, 1.0/p3, 1.0]
        ]
        
        # Melempar matriks ke mesin AHP untuk dihitung bobot dan CR-nya
        ahp_result = calculate_ahp(matrix)
        
    # Melempar variabel ahp_result ke HTML (nilainya None jika halamannya baru dibuka)
    return render_template('admin_ahp.html', ahp_result=ahp_result)

@app.route('/admin/model')
def admin_model():
    return render_template('admin_model.html')

@app.route('/admin/tambah', methods=['POST'])
def admin_tambah():
    # Menangkap semua inputan dari Form Tambah Data HTML
    data_baru = {
        'provinsi': request.form.get('provinsi'),
        'kab_kota': request.form.get('kab_kota'),
        'p0': float(request.form.get('p0', 0)),
        'lama_sekolah': float(request.form.get('lama_sekolah', 0)),
        'pengeluaran': float(request.form.get('pengeluaran', 0)),
        'ipm': float(request.form.get('ipm', 0)),
        'harapan_hidup': float(request.form.get('harapan_hidup', 0)),
        'sanitasi': float(request.form.get('sanitasi', 0)),
        'air_minum': float(request.form.get('air_minum', 0)),
        'tpt': float(request.form.get('tpt', 0)),
        'tpak': float(request.form.get('tpak', 0))
    }
    # Panggil fungsi SQL
    tambah_wilayah(data_baru)
    # Refresh halaman tabel secara otomatis
    return redirect(url_for('admin_data'))

@app.route('/admin/hapus/<kab_kota>', methods=['POST'])
def admin_hapus(kab_kota):
    # Panggil fungsi hapus SQL
    hapus_wilayah(kab_kota)
    return redirect(url_for('admin_data'))

@app.route('/admin/run_pipeline', methods=['POST'])
def admin_run_pipeline():
    # 1. Tarik data mentah dari DB
    df = load_data()
    
    # 2. Siapkan parameter kriteria
    criteria_cols = ['P0', 'Lama_Sekolah', 'Pengeluaran', 'IPM', 'Harapan_Hidup', 'Sanitasi', 'Air_Minum', 'TPT', 'TPAK']
    types = ['benefit', 'cost', 'cost', 'cost', 'cost', 'cost', 'cost', 'benefit', 'cost']
    weights = [0.25, 0.10, 0.10, 0.15, 0.10, 0.05, 0.05, 0.15, 0.05]
    
    # 3. Eksekusi Mesin
    df_saw = calculate_saw(df, criteria_cols, weights, types)
    df_final, _ = apply_kmeans(df_saw, num_clusters=3)
    
    # 4. SIMPAN PERMANEN KE MYSQL
    simpan_hasil_model(df_final)
    
    # Kembali ke halaman panel model
    return redirect(url_for('admin_model'))

if __name__ == '__main__':
    app.run(debug=True)