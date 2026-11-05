# Kalimantan Wildfire Intelligence

Aplikasi Streamlit untuk clustering karakteristik termal hotspot. Proyek ini memakai Python 3.12 64-bit dan membandingkan K-Means dengan Agglomerative Clustering. Aplikasi sudah memiliki dataset bawaan, sehingga dapat langsung dijalankan tanpa mengunggah data lagi.

## 1. Persiapan Windows 11 dan VSCode

1. Ekstrak seluruh ZIP ke folder, misalnya `D:\Kuliah\Hotspot_Kalimantan`. Jangan menjalankan file dari dalam ZIP.
2. Pastikan Python 3.12 **64-bit** tersedia. Anda dapat memakai Python 3.12 64-bit yang sudah digunakan untuk proyek sebelumnya. Periksa lewat Terminal: `py -3.12 --version`.
3. Di VSCode, buka menu **File > Open Folder** dan pilih folder yang langsung berisi `app.py`, `analysis.py`, `requirements.txt`, dan folder `data`.
4. Pasang ekstensi **Python** dari Microsoft pada menu Extensions di VSCode.
5. Buka **Terminal > New Terminal**. Pastikan terminal berada pada folder proyek. Jika perlu, jalankan `cd "D:\Kuliah\Hotspot_Kalimantan"` dengan menyesuaikan lokasi sebenarnya.

## 2. Instalasi pertama

Jalankan perintah berikut satu per satu pada terminal VSCode. Cara ini tidak memerlukan aktivasi PowerShell, sehingga menghindari masalah ExecutionPolicy.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Browser biasanya terbuka otomatis. Jika belum, buka `http://localhost:8501` atau Local URL yang ditampilkan terminal. Biarkan terminal tetap berjalan selama aplikasi digunakan. Hentikan server dengan **Ctrl+C**.

Di VSCode tekan **Ctrl+Shift+P > Python: Select Interpreter > Enter interpreter path**, lalu pilih `.venv\Scripts\python.exe` dalam proyek. Tombol Run Python File biasa bukan cara menjalankan aplikasi ini. Gunakan perintah `python -m streamlit run app.py` melalui interpreter proyek.

## 3. Menjalankan kembali pada hari berikutnya

Buka folder proyek di VSCode dan terminal baru, lalu jalankan satu perintah:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Tidak perlu menginstal ulang paket setiap kali menjalankan aplikasi.

## 4. Cara mengerjakan eksperimen di aplikasi

1. Pilih **Dataset bawaan**. Biarkan semua provinsi dan instrumen terpilih.
2. Biarkan **Transformasi log1p pada FRP** aktif dan pilihan hasil **Otomatis: silhouette tertinggi**.
3. Pastikan angka awal: 180 observasi, K-Means, k=2, silhouette sekitar 0,3697. Perbedaan kecil dapat terjadi antarversi pustaka.
4. Buka **01 Business Objective** untuk menjelaskan masalah, tujuan, dan manfaat penelitian.
5. Buka **02 Data Overview**, baca contoh data serta audit. Bedakan data hotspot, cuaca, dan deret waktu.
6. Buka **03 EDA** untuk membaca distribusi tiga fitur dan jumlah observasi per provinsi. Jelaskan dominasi Kalimantan Tengah.
7. Buka **04 Feature Engineering**. Jelaskan alasan memakai brightness, bright_t31, log1p(frp), lalu standardisasi.
8. Buka **05 Modelling & Evaluation**. Catat tabel konfigurasi k=2–6, profil cluster, dan proyeksi PCA.
9. Pilih hasil **Manual**, lalu bandingkan K-Means k=2 dengan Agglomerative k=2. Gunakan silhouette lebih tinggi dan Davies–Bouldin lebih rendah sebagai petunjuk, disertai profil kelompok.
10. Uji filter **VIIRS** saja, kemudian **MODIS** saja. Catat bahwa sampel MODIS hanya 26 observasi. Kembalikan semua filter sebelum membandingkan dengan angka pada PPT.
11. Nonaktifkan log1p FRP untuk melihat sensitivitas. Catat pengaturan yang digunakan setiap kali menyimpan hasil.
12. Klik **Unduh hasil cluster CSV**, **Unduh evaluasi CSV**, dan **Unduh profil CSV**. Buat nama berkas berbeda untuk setiap skenario agar hasil tidak tertukar.

Nomor cluster tidak menyatakan tingkat bahaya. Hasil ini menjelaskan kemiripan karakteristik termal. Evaluasi pada sampel yang sama belum membuktikan generalisasi ke periode lain.

## 5. Cara upload CSV ke aplikasi yang sedang berjalan

1. Pada sidebar, ubah **Sumber data** menjadi **Unggah CSV**.
2. Klik **Browse files** dan pilih `kalimantan_hotspots_latest.csv`, atau seret file ke kotak unggahan.
3. CSV wajib memiliki kolom `brightness`, `bright_t31`, dan `frp` dengan nilai numerik lengkap. FRP harus nonnegatif.
4. Kolom `province`, `instrument`, `latitude`, `longitude`, serta `hazard_severity` opsional. Jika ada, aplikasi menyediakan filter atau visualisasi yang sesuai.
5. Gunakan minimal 8 dan maksimal 3.000 observasi setelah filter. Batas ini menjaga perhitungan demo tetap ringan. Batas ukuran unggahan 10 MB.
6. CSV cuaca dan deret waktu bukan input utama menu ini. Kedua file bawaan hanya menjadi konteks dan audit.

Unggah CSV pada aplikasi berbeda dengan menerbitkan aplikasi. Berkas unggahan diproses di sesi aplikasi dan tidak ditulis ke repositori oleh kode ini.

## 6. Menerbitkan aplikasi ke Streamlit Community Cloud

Proyek siap untuk diunggah, tetapi belum diterbitkan ke akun Anda. Siapkan akun GitHub dan Streamlit Community Cloud.

1. Masuk ke GitHub dan buat repository baru, misalnya `kalimantan-wildfire-ml`. Pilih visibilitas sesuai ketentuan sumber data. Jika repository publik, file di dalamnya dapat dilihat publik.
2. Buka repository, pilih **Add file > Upload files**.
3. Unggah `app.py`, `analysis.py`, `requirements.txt`, folder `data` beserta tiga CSV, dan README. Sertakan `.streamlit/config.toml` jika ingin tema yang disediakan. Jangan unggah `.venv` atau folder `__pycache__`.
4. Pastikan `app.py` berada pada root repository. Jika proyek berada dalam subfolder, nanti masukkan path lengkap seperti `streamlit_project/app.py` sebagai entrypoint.
5. Commit file. Pastikan struktur dan nama huruf besar/kecil tetap sama, terutama folder `data`.
6. Buka https://share.streamlit.io dan masuk/hubungkan akun GitHub Anda.
7. Klik **Create app**, pilih repository dan branch yang berisi proyek, lalu isi **Main file path** dengan `app.py` jika berada di root.
8. Pada **Advanced settings**, pilih Python **3.12**. Aplikasi ini tidak membutuhkan API key atau secrets.
9. Klik **Deploy** dan tunggu instalasi dependensi. Jika gagal, baca log dan periksa entrypoint, requirements.txt, dan lokasi CSV.
10. Setelah berhasil, buka URL `*.streamlit.app` yang diberikan layanan. Uji dataset bawaan serta mode Unggah CSV, kemudian salin URL itu untuk tugas atau presentasi.

Community Cloud mengambil kode dari repository GitHub. Mengunggah ZIP langsung ke kotak uploader CSV tidak menerbitkan aplikasi. Tampilan menu layanan dapat berubah. Rujukan: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## 7. Urutan demonstrasi untuk paparan

1. Tampilkan tujuan dan alasan memilih clustering.
2. Tampilkan data overview dan temuan audit.
3. Jelaskan EDA dan perbedaan instrumen.
4. Jelaskan transformasi fitur.
5. Tampilkan perbandingan model dan dua profil kelompok.
6. Demonstrasikan unggah CSV yang sama, filter VIIRS, lalu unduh hasil.
7. Tutup dengan keterbatasan data dan kebutuhan validasi.

PPT mengikuti urutan: Business Objective, Data Overview, EDA, Feature Engineering, Modelling & Evaluation. Grafik dan angka pada PPT memakai seluruh dataset bawaan dengan log1p FRP aktif.

## 8. Pemecahan masalah

| Masalah | Langkah perbaikan |
|---|---|
| `py` tidak dikenali | Gunakan lokasi Python 3.12 yang terpasang atau instal Python Launcher, lalu buka ulang terminal |
| Python 3.12 tidak ditemukan | Instal Python 3.12 64-bit atau sesuaikan perintah ke versi kompatibel yang tersedia |
| `No module named streamlit` | Jalankan instalasi requirements dengan interpreter `.venv\Scripts\python.exe` yang sama |
| `requirements.txt` atau `app.py` tidak ditemukan | Buka folder proyek yang langsung berisi file tersebut dan periksa posisi terminal |
| PowerShell melarang Activate.ps1 | Gunakan perintah interpreter langsung pada bagian instalasi, tanpa aktivasi |
| Port 8501 terpakai | Jalankan `.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502` |
| Filter membuat data terlalu sedikit | Pilih lebih banyak provinsi/instrumen sampai minimal 8 observasi |
| CSV berisi satu kolom saja | Simpan ulang sebagai CSV pemisah koma, bukan titik koma |
| Grafik peta tidak tampil | Periksa koneksi internet. PCA dan tabel tetap dapat digunakan |
| Angka berbeda dari PPT | Kembalikan semua provinsi/instrumen, aktifkan log1p FRP, pilih otomatis, dan gunakan CSV bawaan |

## Struktur proyek

| Path | Fungsi |
|---|---|
| `app.py` | Antarmuka Streamlit |
| `analysis.py` | Validasi dan algoritma clustering |
| `requirements.txt` | Dependensi Python |
| `data/` | Tiga CSV asli |
| `.streamlit/config.toml` | Tema dan batas unggahan |
| `Paparan_Hotspot_Kalimantan.pptx` | Bahan presentasi |
| `Panduan_Streamlit_VSCode.html` | Panduan yang dapat dibuka di browser |

Sumber metode: https://scikit-learn.org/stable/modules/clustering.html dan https://scikit-learn.org/stable/modules/preprocessing.html

Panduan instalasi resmi: https://docs.streamlit.io/get-started/installation/command-line
