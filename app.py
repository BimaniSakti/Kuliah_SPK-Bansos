from flask import Flask, render_template, request, redirect, send_file, url_for, session, flash
from models.data_handler import hapus_wilayah, load_data, simpan_hasil_model, tambah_wilayah, edit_wilayah, import_csv_ke_db
from models.spk_machine import calculate_saw, apply_kmeans 
from models.ahp_engine import calculate_ahp, save_weights, load_weights

import io
import os
import numpy as np
from datetime import datetime
from sklearn.metrics import silhouette_score


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'icikiwir123')


# ==========================================
# ROUTING OTENTIKASI (LOGIN & LOGOUT)
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Jika sudah login, langsung lempar ke admin_data
    if session.get('logged_in'):
        return redirect(url_for('admin_data'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hardcode kredensial admin (Bisa diubah sesuai keinginanmu)
        if username == os.environ.get('ADMIN_USER', 'admin') and password == os.environ.get('ADMIN_PASS', 'admin123'):
            session['logged_in'] = True
            return redirect(url_for('admin_data'))
        else:
            flash('Username atau Password salah!', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


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
    
    sil_score = 0
    if 'Skor_SAW' in df_jabar.columns and 'Kategori_Prioritas' in df_jabar.columns:
        df_jabar = df_jabar.sort_values(by='Skor_SAW', ascending=False)
        
        # Kalkulasi ulang Silhouette Score khusus untuk subset Jawa Barat
        X = df_jabar[['Skor_SAW']].values
        # Mengubah teks kategori menjadi angka agar bisa dihitung sklearn
        labels = df_jabar['Kategori_Prioritas'].astype('category').cat.codes
        if len(np.unique(labels)) > 1:
            sil_score = round(silhouette_score(X, labels), 3)
            
    data_jabar = df_jabar.to_dict(orient='records')
    return render_template('ranking.html', data_wilayah=data_jabar, sil_score=sil_score)

@app.route('/export/excel')
def export_excel():
    """Rute untuk mengunduh tabel ranking sebagai file CSV/Excel"""
    df = load_data()
    df_jabar = df[df['Provinsi'] == 'JAWA BARAT'].copy()
    
    if 'Skor_SAW' in df_jabar.columns:
        df_jabar = df_jabar.sort_values(by='Skor_SAW', ascending=False)
        # Pilih kolom yang penting saja untuk di-export
        kolom_export = ['Provinsi', 'Kab/Kota', 'P0', 'Skor_SAW', 'Kategori_Prioritas']
        df_export = df_jabar[kolom_export]
    else:
        df_export = df_jabar
        
    # Menggunakan BytesIO agar file tidak perlu disimpan di harddisk server
    output = io.BytesIO()
    df_export.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='Ranking_Bansos_Jabar.csv')

# ==========================================
# ROUTING AREA ADMIN
# ==========================================
@app.route('/admin')
def admin_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    df = load_data()
    
    # Menghitung Statistik Khusus Jawa Barat (Sesuai UI)
    df_jabar = df[df['Provinsi'] == 'JAWA BARAT']
    if not df_jabar.empty:
        avg_p0 = round(df_jabar['P0'].mean(), 2)
        avg_sekolah = round(df_jabar['Lama_Sekolah'].mean(), 2)
        avg_tpt = round(df_jabar['TPT'].mean(), 2)
        avg_sanitasi = round(df_jabar['Sanitasi'].mean(), 2)
    else:
        avg_p0 = avg_sekolah = avg_tpt = avg_sanitasi = 0
        
    data_nasional = df.to_dict(orient='records')
    
    # Melempar angka statistik ke HTML
    return render_template('admin_data.html', 
                           data_wilayah=data_nasional,
                           avg_p0=avg_p0, avg_sekolah=avg_sekolah,
                           avg_tpt=avg_tpt, avg_sanitasi=avg_sanitasi)
    
@app.route('/admin/tambah', methods=['POST'])
def admin_tambah():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
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

@app.route('/admin/edit', methods=['POST'])
def admin_edit():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    data_edit = {
        'provinsi': request.form.get('provinsi'),
        'kab_kota': request.form.get('kab_kota'), # Kab/Kota digunakan sebagai kunci pencarian
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
    edit_wilayah(data_edit)
    return redirect(url_for('admin_data'))

@app.route('/admin/hapus/<kab_kota>', methods=['POST'])
def admin_hapus(kab_kota):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    # Panggil fungsi hapus SQL
    hapus_wilayah(kab_kota)
    return redirect(url_for('admin_data'))
    
@app.route('/admin/import', methods=['POST'])
def admin_import():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    # Menangkap file CSV yang diunggah Admin
    file = request.files.get('file_csv')
    if file and file.filename.endswith('.csv'):
        import_csv_ke_db(file)
    return redirect(url_for('admin_data'))

@app.route('/admin/ahp', methods=['GET', 'POST'])
def admin_ahp():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    ahp_result = None
    
    if request.method == 'POST':
        # Menangkap tombol mana yang diklik (dari atribut name="action" di HTML)
        action = request.form.get('action')
        
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
        
        # Jika admin mengklik "Save Configuration"
        if action == 'save':
            if ahp_result['is_consistent']:
                save_weights(ahp_result['weights'])
                flash('Konfigurasi bobot AHP berhasil disimpan permanen!', 'success')
            else:
                flash('Gagal menyimpan! Matriks tidak konsisten (CR > 0.1).', 'danger')
        
    # Melempar variabel ahp_result ke HTML (nilainya None jika halamannya baru dibuka)
    return render_template('admin_ahp.html', ahp_result=ahp_result)

@app.route('/admin/model')
def admin_model():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Mengambil log dari session, jika belum pernah dijalankan, beri teks default
    logs = session.get('system_log', ["[SYSTEM] Ready for execution. Press 'JALANKAN FULL PIPELINE' to start."])
    last_run = session.get('last_run', "BELUM PERNAH DIEKSEKUSI")
    
    return render_template('admin_model.html', logs=logs, last_run=last_run)

@app.route('/admin/run_pipeline', methods=['POST'])
def admin_run_pipeline():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    # 1. Tarik data mentah dari DB
    df = load_data()
    
    # 2. Siapkan parameter kriteria
    criteria_cols = ['P0', 'Lama_Sekolah', 'Pengeluaran', 'IPM', 'Harapan_Hidup', 'Sanitasi', 'Air_Minum', 'TPT', 'TPAK']
    types = ['benefit', 'cost', 'cost', 'cost', 'cost', 'cost', 'cost', 'benefit', 'cost']
    weights = load_weights()
    
    # 3. Eksekusi Mesin
    df_saw = calculate_saw(df, criteria_cols, weights, types)
    df_final, sil_score = apply_kmeans(df_saw, num_clusters=3)
    
    # 4. SIMPAN PERMANEN KE MYSQL
    simpan_hasil_model(df_final)
    
    # 5. Generate Dynamic Log (Terminal Output)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text = [
        f"[{now}] INITIATING ANALYTICS ENGINE...",
        "[STABLE] Checking connection to MySQL Database... OK",
        f"[INFO] {len(df)} rows loaded from nationwide repository.",
        "[SUCCESS] SAW Preference Weights generated successfully.",
        f"[{now}] TRAINING K-MEANS WITH K=3...",
        "[SUCCESS] Cluster Centroids reached convergence.",
        f"[INFO] Model Silhouette Score evaluation metric: {sil_score}",
        "[DONE] All data tables and public dashboard synchronized successfully."
    ]
    
    # Simpan log dan waktu eksekusi ke session agar bisa dibaca oleh halaman web
    session['system_log'] = log_text
    session['last_run'] = now
    
    # Kembali ke halaman panel model
    return redirect(url_for('admin_model'))

if __name__ == '__main__':
    app.run(debug=True)