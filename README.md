# SIPAWAS (Sistem Pelaporan Pengawasan Lapangan)
### Dinas Perumahan dan Permukiman (DISPERKIM)

SIPAWAS adalah aplikasi berbasis web internal yang dirancang untuk memfasilitasi pengawas lapangan di Dinas Perumahan dan Permukiman dalam mengirimkan laporan hasil pengawasan kegiatan secara mandiri. Aplikasi ini bertujuan menghilangkan proses input ulang (double entry) data oleh Admin, mempercepat verifikasi laporan, dan menyediakan visualisasi rekapitulasi data yang transparan bagi pimpinan.

---

## 🚀 Fitur Utama

- **Akses Berbasis Peran (RBAC)**: Mendukung role *Super Admin*, *Admin*, *Pengawas Lapangan*, dan *Pimpinan*.
- **Pelaporan Lapangan Mandiri**: Input laporan kegiatan bulanan, progres pelaksanaan, kendala, dan unggah multi-file dokumentasi (Foto/PDF).
- **Alur Verifikasi Dua Arah**: Admin dapat menyetujui laporan (*Terverifikasi*) atau mengembalikannya (*Perlu Revisi*) disertai catatan perbaikan.
- **Audit Trail (Riwayat Status)**: Melacak jejak riwayat status setiap laporan secara transparan.
- **Dashboard Visual**: Grafik statistik penyebaran status, sebaran laporan bulanan, dan keaktifan pengawas menggunakan **Chart.js**.
- **Ekspor Data Rekap**:
  - **Excel**: Mengunduh data terverifikasi dalam format `.xlsx` rapi via `openpyxl`.
  - **PDF**: Pratinjau cetak resmi berformat Kop Surat Dinas dan kolom tanda tangan pengawas & PPTK.
- **Sistem Notifikasi**: Pemberitahuan *in-app* otomatis untuk pengajuan laporan baru dan pembaruan status laporan.

---

## 🛠️ Spesifikasi Teknologi

- **Backend**: Django (Python 3.14+)
- **Frontend**: Django Templates + Bootstrap 5 + Vanilla CSS/JS
- **Visualisasi**: Chart.js (via CDN)
- **Database**: SQLite3 (Dukungan penuh migrasi PostgreSQL/MySQL via `.env`)
- **Pustaka Ekspor**: openpyxl

---

## ⚙️ Petunjuk Pemasangan & Menjalankan Lokal

Ikuti langkah-langkah berikut untuk menjalankan aplikasi SIPAWAS di komputer lokal Anda:

### 1. Prasyarat
Pastikan komputer Anda sudah terpasang **Python** (versi 3.10 ke atas) dan **pip**.

### 2. Siapkan Virtual Environment
Buka terminal/PowerShell di direktori proyek, lalu buat dan aktifkan *virtual environment*:
```powershell
# Membuat virtual environment (.venv)
python -m venv .venv

# Mengaktifkan di Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Mengaktifkan di Windows (CMD)
.\.venv\Scripts\activate.bat

# Mengaktifkan di Linux/macOS
source .venv/bin/activate
```

### 3. Pasang Dependensi
Pasang seluruh dependensi pustaka yang dibutuhkan:
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment Variables (`.env`)
Berkas konfigurasi `.env` telah disediakan di direktori utama dengan isi default sebagai berikut:
```env
DEBUG=True
SECRET_KEY=django-insecure-sipawas-secret-key-1234567890
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### 5. Jalankan Migrasi Database
Buat skema tabel database berdasarkan model Django yang ada:
```bash
python manage.py makemigrations pelaporan
python manage.py migrate
```

### 6. Masukkan Data Demo Awal (Seeding)
Gunakan perintah kustom untuk memasukkan data master awal (akun pengguna uji coba, data PPTK, dan beberapa data Kegiatan):
```bash
python manage.py seed_data
```

### 7. Jalankan Server Pembangunan
Nyalakan server lokal Django:
```bash
python manage.py runserver
```
Buka browser Anda dan akses aplikasi melalui alamat: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Akun Demo Pengujian

Setelah menjalankan `seed_data`, Anda dapat masuk menggunakan salah satu akun berikut:

| No | Username | Password | Role / Peran | Nama Pengguna |
|:---:|---|---|---|---|
| 1 | `superadmin` | `admin123` | **Super Admin** | Super Admin |
| 2 | `admin` | `admin123` | **Admin (Verifikator)** | Rian Hidayat |
| 3 | `pengawas1` | `pengawas123` | **Pengawas Lapangan** | Budi Santoso |
| 4 | `pengawas2` | `pengawas123` | **Pengawas Lapangan** | Siti Aminah |
| 5 | `pimpinan` | `pimpinan123` | **Pimpinan (Read-Only)** | Drs. Heru Prasetyo, M.Si |

---

## 📁 Struktur Proyek Utama
```text
Sistem Pelaporan DISPERKIM/
│
├── sipawas/                 # Pengaturan utama proyek Django
│   ├── settings.py          # Konfigurasi aplikasi, database, static, dll.
│   ├── urls.py              # Routing URL utama proyek
│   └── ...
│
├── pelaporan/               # Aplikasi utama (core app)
│   ├── management/          # Perintah kustom Django (seed_data)
│   ├── models.py            # Skema tabel database (User, Kegiatan, Laporan, dll.)
│   ├── views.py             # Logika bisnis controller
│   ├── forms.py             # Validasi input formulir
│   ├── decorators.py        # Custom middleware / hak akses role
│   ├── context_processors.py# Penghitung notifikasi global
│   └── urls.py              # Routing URL aplikasi
│
├── templates/               # Berkas HTML Django Templates
│   ├── auth/                # Halaman login
│   ├── dashboard/           # Dashboard Pengawas & Admin
│   ├── laporan/             # Formulir input, list, dan detail laporan
│   ├── master/              # CRUD PPTK, Kegiatan, dan Pengguna
│   ├── rekap/               # Halaman Rekap & Pratinjau Cetak PDF
│   └── base.html            # Kerangka tata letak utama
│
├── static/                  # Aset statis kustom
│   └── css/style.css        # Desain gaya visual premium
│
├── requirements.txt         # Daftar dependensi pustaka Python
├── .env                     # Variabel konfigurasi lingkungan lokal
└── README.md                # Dokumentasi proyek ini
```
