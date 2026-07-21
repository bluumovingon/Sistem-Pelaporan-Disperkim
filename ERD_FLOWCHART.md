# 📐 Dokumentasi ERD & Flowchart - SIPAWAS (Sistem Pelaporan Disperkim)

Dokumentasi ini berisi **Entity Relationship Diagram (ERD)**, **Flowchart Alur Kerja (Workflows)**, serta **Spesifikasi Basis Data** untuk aplikasi **SIPAWAS** (*Sistem Pelaporan Pelaksanaan Kegiatan Dinas Perkim*).

---

## 📑 Daftar Isi
1. [Entity Relationship Diagram (ERD)](#1-entity-relationship-diagram-erd)
2. [Flowchart Sistem](#2-flowchart-sistem)
   - [A. Alur Pengajuan & Verifikasi Laporan](#a-flowchart-alur-pengajuan--verifikasi-laporan-core-process)
   - [B. Alur Persetujuan Usulan Kegiatan](#b-flowchart-persetujuan-usulan-kegiatan-baru-master-data)
   - [C. Alur Autentikasi & Hak Akses (RBAC)](#c-flowchart-autentikasi--hak-akses-pengguna-rbac)
3. [Spesifikasi Tabel Database](#3-spesifikasi-tabel-database)
4. [Matriks Hak Akses Pengguna (Role Matrix)](#4-matriks-hak-akses-pengguna-role-matrix)

---

## 1. Entity Relationship Diagram (ERD)

Diagram berikut menjelaskan entitas, atribut, tipe data, serta hubungan antar tabel pada database Django.

```mermaid
erDiagram
    User {
        int id PK
        string username
        string password
        string first_name
        string last_name
        string email
        string role "super_admin | admin | pptk | pimpinan"
        string jabatan
        string unit_kerja
        boolean status_aktif
    }

    Kegiatan {
        int id PK
        int pptk_id FK
        string judul_kegiatan
        int tahun
        float latitude
        float longitude
        string status "diajukan | disetujui | ditolak"
        string catatan_admin
    }

    Laporan {
        int id PK
        int kegiatan_id FK
        int pptk_id FK
        string bulan_laporan "Januari - Desember"
        string tahapan_pelaksanaan
        string kendala
        string status "draft | diajukan | terverifikasi | perlu_revisi"
        string catatan_revisi
        float latitude
        float longitude
        datetime created_at
        datetime updated_at
    }

    Dokumentasi {
        int id PK
        int laporan_id FK
        string file "JPG/PNG/PDF (Max 5MB)"
        string keterangan
    }

    RiwayatStatus {
        int id PK
        int laporan_id FK
        int diubah_oleh_id FK
        string status_lama
        string status_baru
        string catatan
        datetime created_at
    }

    Notifikasi {
        int id PK
        int user_id FK
        int laporan_id FK
        string judul
        string pesan
        boolean is_read
        datetime created_at
    }

    User ||--o{ Kegiatan : "mengelola (PPTK)"
    User ||--o{ Laporan : "membuat (PPTK)"
    User ||--o{ RiwayatStatus : "melakukan_perubahan"
    User ||--o{ Notifikasi : "menerima"
    Kegiatan ||--o{ Laporan : "memiliki"
    Laporan ||--o{ Dokumentasi : "memiliki_lampiran"
    Laporan ||--o{ RiwayatStatus : "memiliki_histori"
    Laporan ||--o{ Notifikasi : "memicu"
```

---

## 2. Flowchart Sistem

### A. Flowchart Alur Pengajuan & Verifikasi Laporan (Core Process)

Diagram ini menggambarkan alur kerja pembuatan laporan oleh **PPTK**, validasi keamanan berkas (*Magic Bytes File Signature*), hingga proses verifikasi/revisi oleh **Admin**.

```mermaid
flowchart TD
    Start([Mulai: PPTK Akses Sistem]) --> Login[Login PPTK]
    Login --> Dashboard[Dashboard PPTK]
    Dashboard --> FormLaporan[Isi Form Laporan Pelaksanaan Kegiatan]
    
    FormLaporan --> UploadFile[Upload Dokumen Foto/PDF]
    UploadFile --> ValFormat{Validasi Ekstensi & Ukuran?\nJPG/PNG/PDF <= 5MB}
    
    ValFormat -- Tidak --> ErrFile[Tampilkan Error File Tidak Valid]
    ErrFile --> FormLaporan
    
    ValFormat -- Ya --> ValSig{Validasi Magic Bytes\nFile Signature?}
    ValSig -- Palsu/Berbahaya --> ErrSig[Tampilkan Error Berkas Ditolak]
    ErrSig --> FormLaporan
    
    ValSig -- Valid --> ChoiceSimpan{Pilihan Aksi?}
    
    ChoiceSimpan -- Simpan Draft --> SaveDraft[Simpan Laporan Status: 'draft']
    SaveDraft --> EndDraft([Selesai: Laporan Disimpan sebagai Draft])
    
    ChoiceSimpan -- Ajukan --> SaveSubmit[Simpan Laporan Status: 'diajukan']
    SaveSubmit --> NotifAdmin[Kirim Notifikasi ke Admin]
    NotifAdmin --> WaitVerif([Menunggu Verifikasi Admin])

    WaitVerif --> AdminVerif[Admin/Super Admin Buka Detail Laporan]
    AdminVerif --> Decision{Hasil Verifikasi Admin?}
    
    Decision -- Setujui --> Approve[Ubah Status: 'terverifikasi']
    Approve --> LogHistory1[Catat di RiwayatStatus]
    LogHistory1 --> SendNotifPPTK1[Kirim Notifikasi 'Laporan Disetujui' ke PPTK]
    SendNotifPPTK1 --> EndApprove([Selesai: Laporan Terverifikasi])

    Decision -- Perlu Revisi --> Reject[Isi Catatan Revisi & Ubah Status: 'perlu_revisi']
    Reject --> LogHistory2[Catat di RiwayatStatus]
    LogHistory2 --> SendNotifPPTK2[Kirim Notifikasi 'Perlu Revisi' ke PPTK]
    SendNotifPPTK2 --> PPTKEdit[PPTK Memperbaiki Laporan & Kirim Ulang]
    PPTKEdit --> WaitVerif
```

---

### B. Flowchart Persetujuan Usulan Kegiatan Baru (Master Data)

Diagram ini menggambarkan alur penambahan data kegiatan baru oleh PPTK maupun Admin.

```mermaid
flowchart TD
    StartK([Mulai: Tambah Kegiatan Baru]) --> CheckRole{Role Pengguna?}
    
    CheckRole -- Admin / Super Admin --> AdminInput[Input Data Kegiatan & Koordinat Map]
    AdminInput --> DirectApprove[Status Langsung: 'disetujui']
    DirectApprove --> SaveK1[Simpan Data Kegiatan] --> EndK1([Selesai: Kegiatan Aktif])

    CheckRole -- PPTK --> PPTKInput[PPTK Ajukan Usulan Kegiatan Baru]
    PPTKInput --> StatusDiajukan[Status Awal: 'diajukan']
    StatusDiajukan --> SaveK2[Simpan Usulan Kegiatan]
    SaveK2 --> AdminReview[Admin Review Usulan Kegiatan]
    
    AdminReview --> AdminDecision{Keputusan Admin?}
    AdminDecision -- Setujui --> ApproveK[Ubah Status: 'disetujui'] --> EndK2([Selesai: Kegiatan Aktif])
    AdminDecision -- Tolak --> RejectK[Isi Catatan Admin & Status: 'ditolak'] --> EndK3([Selesai: Usulan Ditolak])
```

---

### C. Flowchart Autentikasi & Hak Akses Pengguna (RBAC)

Diagram ini menggambarkan alur autentikasi login, fitur keamanan *Rate Limiting IP*, serta pembagian halaman dashboard berdasarkan hak akses role.

```mermaid
flowchart TD
    StartAuth([Pengunjung Buka Website]) --> FormLogin[Tampilkan Form Login]
    FormLogin --> SubmitLogin[Input Username & Password]
    
    SubmitLogin --> RateLimit{Percobaan Login > 5x\ndalam 15 Menit?}
    RateLimit -- Ya --> Lockout[Tampilkan Error Lockout 15 Menit] --> FormLogin
    
    RateLimit -- Tidak --> AuthCheck{Username & Password\nSesuai?}
    AuthCheck -- Salah --> IncAttempt[Tambah Hits Gagal Login] --> FormLogin
    
    AuthCheck -- Benar --> RoleCheck{Cek Role Pengguna}
    
    RoleCheck -- Super Admin / Admin --> DashAdmin[Redirect: Dashboard Admin & Rekapitulasi]
    RoleCheck -- PPTK --> DashPPTK[Redirect: Dashboard PPTK & Input Laporan]
    RoleCheck -- Pimpinan --> DashPimpinan[Redirect: Dashboard Pimpinan & Cetak PDF/Excel]
    
    DashAdmin --> EndUser([Selesai: Pengguna Beraktivitas])
    DashPPTK --> EndUser
    DashPimpinan --> EndUser
```

---

## 3. Spesifikasi Tabel Database

### 1. Tabel `User` (`pelaporan_user`)
| Field | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `id` | BigAutoField (PK) | Primary Key |
| `username` | VarChar(150) | Unique ID pengguna |
| `password` | VarChar(128) | Hashed password |
| `role` | VarChar(20) | Enum: `super_admin`, `admin`, `pptk`, `pimpinan` |
| `jabatan` | VarChar(100) | Jabatan struktural |
| `unit_kerja` | VarChar(100) | Bidang / Unit kerja |
| `status_aktif` | Boolean | True jika akun aktif |

### 2. Tabel `Kegiatan` (`pelaporan_kegiatan`)
| Field | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `id` | BigAutoField (PK) | Primary Key |
| `pptk_id` | ForeignKey (User) | Penanggung jawab PPTK |
| `judul_kegiatan` | VarChar(255) | Nama paket/kegiatan |
| `tahun` | Integer | Tahun anggaran |
| `latitude` | Float (Nullable) | Koordinat peta |
| `longitude` | Float (Nullable) | Koordinat peta |
| `status` | VarChar(20) | Enum: `diajukan`, `disetujui`, `ditolak` |
| `catatan_admin` | Text | Catatan persetujuan/penolakan admin |

### 3. Tabel `Laporan` (`pelaporan_laporan`)
| Field | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `id` | BigAutoField (PK) | Primary Key |
| `kegiatan_id` | ForeignKey (Kegiatan) | Paket kegiatan terkait |
| `pptk_id` | ForeignKey (User) | Pembuat laporan |
| `bulan_laporan` | VarChar(20) | Bulan pelaksanaan |
| `tahapan_pelaksanaan` | Text | Uraian capaian fisik/pekerjaan |
| `kendala` | Text | Kendala lapangan (jika ada) |
| `status` | VarChar(20) | Enum: `draft`, `diajukan`, `terverifikasi`, `perlu_revisi` |
| `catatan_revisi` | Text | Catatan dari admin jika perlu revisi |
| `latitude` | Float (Nullable) | Koordinat lintang dokumentasi lapangan |
| `longitude` | Float (Nullable) | Koordinat bujur dokumentasi lapangan |
| `created_at` | DateTime | Waktu pembuatan |
| `updated_at` | DateTime | Waktu update terakhir |

### 4. Tabel `Dokumentasi` (`pelaporan_dokumentasi`)
| Field | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `id` | BigAutoField (PK) | Primary Key |
| `laporan_id` | ForeignKey (Laporan) | Relasi ke laporan |
| `file` | FileField | Path file foto/PDF terupload |
| `keterangan` | VarChar(255) | Deskripsi singkat foto/berkas |

### 5. Tabel `RiwayatStatus` (`pelaporan_riwayatstatus`)
| Field | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `id` | BigAutoField (PK) | Primary Key |
| `laporan_id` | ForeignKey (Laporan) | Laporan yang diubah |
| `diubah_oleh_id` | ForeignKey (User) | Pengubah status |
| `status_lama` | VarChar(20) | Status sebelum diubah |
| `status_baru` | VarChar(20) | Status setelah diubah |
| `catatan` | Text | Catatan perubahan |
| `created_at` | DateTime | Waktu pencatatan log |

### 6. Tabel `Notifikasi` (`pelaporan_notifikasi`)
| Field | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `id` | BigAutoField (PK) | Primary Key |
| `user_id` | ForeignKey (User) | Penerima notifikasi |
| `laporan_id` | ForeignKey (Laporan) | Laporan terkait (optional) |
| `judul` | VarChar(255) | Judul notifikasi |
| `pesan` | Text | Isi pesan notifikasi |
| `is_read` | Boolean | Status dibaca |
| `created_at` | DateTime | Waktu kirim |

---

## 4. Matriks Hak Akses Pengguna (Role Matrix)

| Fitur / Modul | Super Admin | Admin | PPTK | Pimpinan |
| :--- | :---: | :---: | :---: | :---: |
| **Manajemen Pengguna (User Management)** | ✅ | ✅ | ❌ | ❌ |
| **Kelola Master Data Kegiatan** | ✅ | ✅ | 🟡 (Usul saja) | 👁️ (Lihat) |
| **Persetujuan Usulan Kegiatan** | ✅ | ✅ | ❌ | ❌ |
| **Buat / Edit / Hapus Draft Laporan** | ❌ | ❌ | ✅ (Milik sendiri) | ❌ |
| **Verifikasi & Revisi Laporan** | ✅ | ✅ | ❌ | ❌ |
| **Lihat Dashboard & Rekapitulasi** | ✅ | ✅ | ✅ | ✅ |
| **Cetak PDF & Export Excel** | ✅ | ✅ | ✅ | ✅ |
