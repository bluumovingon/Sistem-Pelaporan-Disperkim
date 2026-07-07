from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from pelaporan.models import User, PPTK, Kegiatan, Laporan, Dokumentasi, RiwayatStatus, Notifikasi

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'first_name', 'last_name', 'email', 'role', 'status_aktif']
    fieldsets = UserAdmin.fieldsets + (
        ('Informasi Tambahan', {'fields': ('role', 'unit_kerja', 'status_aktif')}),
    )

class DokumentasiInline(admin.TabularInline):
    model = Dokumentasi
    extra = 1

class RiwayatStatusInline(admin.TabularInline):
    model = RiwayatStatus
    extra = 0
    readonly_fields = ['status_lama', 'status_baru', 'diubah_oleh', 'catatan', 'created_at']
    can_delete = False

class LaporanAdmin(admin.ModelAdmin):
    list_display = ['id', 'kegiatan', 'pengawas', 'bulan_laporan', 'status', 'updated_at']
    list_filter = ['status', 'bulan_laporan']
    search_fields = ['kegiatan__judul_kegiatan', 'pengawas__username', 'tahapan_pelaksanaan']
    inlines = [DokumentasiInline, RiwayatStatusInline]

admin.site.register(User, CustomUserAdmin)
admin.site.register(PPTK)
admin.site.register(Kegiatan)
admin.site.register(Laporan, LaporanAdmin)
admin.site.register(Dokumentasi)
admin.site.register(RiwayatStatus)
admin.site.register(Notifikasi)
