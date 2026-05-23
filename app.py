from flask import Flask, render_template

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# ==========================================
# ROUTING AREA PUBLIK
# ==========================================

@app.route('/')
def index():
    # Menampilkan Landing Page (Beranda)
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Menampilkan Statistik Visual
    return render_template('dashboard.html')

@app.route('/ranking')
def ranking():
    # Menampilkan Tabel Eksplorasi Ranking
    return render_template('ranking.html')

# ==========================================
# ROUTING AREA ADMIN
# ==========================================

@app.route('/admin')
def admin_data():
    # Menampilkan Halaman Manajemen Data Wilayah (Default Admin)
    return render_template('admin_data.html')

@app.route('/admin/ahp')
def admin_ahp():
    # Menampilkan Halaman Konfigurasi Kriteria AHP
    return render_template('admin_ahp.html')

@app.route('/admin/model')
def admin_model():
    # Menampilkan Halaman Eksekusi Model (SAW & K-Means)
    return render_template('admin_model.html')

# ==========================================
# RUN SERVER
# ==========================================
if __name__ == '__main__':
    # debug=True agar server otomatis restart jika ada perubahan kode
    app.run(debug=True)