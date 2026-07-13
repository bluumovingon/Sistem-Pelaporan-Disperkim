from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime

class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('pptk', 'PPTK'),
        ('pimpinan', 'Pimpinan'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='pptk')
    jabatan = models.CharField(max_length=100, blank=True)
    unit_kerja = models.CharField(max_length=100, blank=True)
    status_aktif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username}) - {self.get_role_display()}"


class Kegiatan(models.Model):
    judul_kegiatan = models.CharField(max_length=255)
    pptk = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kegiatan', limit_choices_to={'role': 'pptk'})
    tahun = models.IntegerField(default=datetime.datetime.now().year)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Kegiatan"
        verbose_name_plural = "Kegiatan"
        
    def __str__(self):
        return f"{self.judul_kegiatan} ({self.tahun})"


class Laporan(models.Model):
    BULAN_CHOICES = (
        ('Januari', 'Januari'),
        ('Februari', 'Februari'),
        ('Maret', 'Maret'),
        ('April', 'April'),
        ('Mei', 'Mei'),
        ('Juni', 'Juni'),
        ('Juli', 'Juli'),
        ('Agustus', 'Agustus'),
        ('September', 'September'),
        ('Oktober', 'Oktober'),
        ('November', 'November'),
        ('Desember', 'Desember'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('diajukan', 'Diajukan'),
        ('terverifikasi', 'Terverifikasi'),
        ('perlu_revisi', 'Perlu Revisi'),
    )
    
    kegiatan = models.ForeignKey(Kegiatan, on_delete=models.CASCADE, related_name='laporan')
    pptk = models.ForeignKey(User, on_delete=models.CASCADE, related_name='laporan_pptk', limit_choices_to={'role': 'pptk'})
    bulan_laporan = models.CharField(max_length=20, choices=BULAN_CHOICES)
    tahapan_pelaksanaan = models.TextField()
    kendala = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    catatan_revisi = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Laporan"
        verbose_name_plural = "Laporan"
        ordering = ['-updated_at']
        
    def __str__(self):
        return f"Laporan {self.kegiatan.judul_kegiatan} - {self.bulan_laporan} ({self.pptk.username})"
        
    @property
    def is_draft(self):
        return self.status == 'draft'
        
    @property
    def is_diajukan(self):
        return self.status == 'diajukan'
        
    @property
    def is_terverifikasi(self):
        return self.status == 'terverifikasi'
        
    @property
    def is_perlu_revisi(self):
        return self.status == 'perlu_revisi'


class Dokumentasi(models.Model):
    laporan = models.ForeignKey(Laporan, on_delete=models.CASCADE, related_name='dokumentasi')
    file = models.FileField(upload_to='dokumentasi/')
    keterangan = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "Dokumentasi"
        verbose_name_plural = "Dokumentasi"
        
    def __str__(self):
        return f"Dokumentasi Laporan {self.laporan.id} - {self.file.name}"


class RiwayatStatus(models.Model):
    laporan = models.ForeignKey(Laporan, on_delete=models.CASCADE, related_name='riwayat_status')
    status_lama = models.CharField(max_length=20, choices=Laporan.STATUS_CHOICES)
    status_baru = models.CharField(max_length=20, choices=Laporan.STATUS_CHOICES)
    diubah_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    catatan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Riwayat Status"
        verbose_name_plural = "Riwayat Status"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Histori Laporan {self.laporan.id}: {self.status_lama} -> {self.status_baru}"


class Notifikasi(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifikasi')
    judul = models.CharField(max_length=255)
    pesan = models.TextField()
    laporan = models.ForeignKey(Laporan, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notifikasi"
        verbose_name_plural = "Notifikasi"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Notifikasi untuk {self.user.username}: {self.judul}"

