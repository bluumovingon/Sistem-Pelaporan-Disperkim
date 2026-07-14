from django.urls import path
from pelaporan import views

urlpatterns = [
    # Auth & Home
    path('', views.home_redirect, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Laporan
    path('laporan/', views.laporan_list_view, name='laporan_list'),
    path('laporan/buat/', views.laporan_buat_view, name='laporan_buat'),
    path('laporan/<int:pk>/', views.laporan_detail_view, name='laporan_detail'),
    path('laporan/<int:pk>/edit/', views.laporan_edit_view, name='laporan_edit'),
    path('laporan/<int:pk>/verifikasi/', views.laporan_verifikasi_view, name='laporan_verifikasi'),
    path('laporan/<int:pk>/hapus/', views.laporan_hapus_view, name='laporan_hapus'),
    path('laporan/dokumentasi/<int:pk>/hapus/', views.dokumentasi_hapus_view, name='dokumentasi_hapus'),
    
    # Rekap & Ekspor
    path('rekap/', views.rekap_view, name='rekap'),
    path('rekap/excel/', views.rekap_excel_view, name='rekap_excel'),
    path('rekap/pdf/<int:pk>/', views.rekap_pdf_view, name='rekap_pdf'),
    
    # Master Kegiatan
    path('master/kegiatan/', views.kegiatan_list_view, name='kegiatan_list'),
    path('master/kegiatan/tambah/', views.kegiatan_tambah_view, name='kegiatan_tambah'),
    path('master/kegiatan/<int:pk>/edit/', views.kegiatan_edit_view, name='kegiatan_edit'),
    path('master/kegiatan/<int:pk>/verifikasi/', views.kegiatan_verifikasi_view, name='kegiatan_verifikasi'),
    path('master/kegiatan/<int:pk>/hapus/', views.kegiatan_hapus_view, name='kegiatan_hapus'),
    
    # Proteksi Media Berkas
    path('media/dokumentasi/<path:filename>', views.serve_dokumentasi_view, name='serve_dokumentasi'),
    
    # Master Pengguna (Super Admin)
    path('master/pengguna/', views.pengguna_list_view, name='pengguna_list'),
    path('master/pengguna/tambah/', views.pengguna_tambah_view, name='pengguna_tambah'),
    path('master/pengguna/<int:pk>/edit/', views.pengguna_edit_view, name='pengguna_edit'),
    path('master/pengguna/<int:pk>/hapus/', views.pengguna_hapus_view, name='pengguna_hapus'),
    
    # Notifikasi
    path('notifikasi/', views.notifikasi_list_view, name='notifikasi_list'),
    path('notifikasi/<int:pk>/baca/', views.notifikasi_baca_view, name='notifikasi_baca'),
    path('notifikasi/baca-semua/', views.notifikasi_baca_semua_view, name='notifikasi_baca_semua'),
]
