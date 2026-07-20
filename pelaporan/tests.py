from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from pelaporan.models import User, Kegiatan, Laporan, Dokumentasi
from pelaporan.utils import validate_file_signature
import io

class SecurityAndLogicTestCase(TestCase):
    def setUp(self):
        # Create users
        self.superadmin = User.objects.create_user(
            username='superadmin', password='password123', role='super_admin'
        )
        self.admin = User.objects.create_user(
            username='admin', password='password123', role='admin'
        )
        self.pptk = User.objects.create_user(
            username='pptk1', password='password123', role='pptk'
        )
        self.pimpinan = User.objects.create_user(
            username='pimpinan1', password='password123', role='pimpinan'
        )
        
        # Create a disetujui Kegiatan for testing
        self.kegiatan = Kegiatan.objects.create(
            judul_kegiatan="Kegiatan Uji Coba",
            pptk=self.pptk,
            tahun=2026,
            status='disetujui'
        )
        
        # Create Laporan
        self.laporan = Laporan.objects.create(
            kegiatan=self.kegiatan,
            pptk=self.pptk,
            bulan_laporan='Januari',
            tahapan_pelaksanaan='Progres awal 10%',
            status='draft'
        )
        
        # Create Dokumentasi
        dummy_file = SimpleUploadedFile("test_photo.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF", content_type="image/jpeg")
        self.dokumentasi = Dokumentasi.objects.create(
            laporan=self.laporan,
            file=dummy_file,
            keterangan="Foto Awal"
        )
        
    def test_file_signature_validation(self):
        # Valid JPEG
        valid_jpeg = SimpleUploadedFile("image.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF", content_type="image/jpeg")
        self.assertTrue(validate_file_signature(valid_jpeg))
        
        # Valid PNG
        valid_png = SimpleUploadedFile("image.png", b"\x89PNG\r\n\x1a\n", content_type="image/png")
        self.assertTrue(validate_file_signature(valid_png))
        
        # Valid PDF
        valid_pdf = SimpleUploadedFile("doc.pdf", b"%PDF-1.4...", content_type="application/pdf")
        self.assertTrue(validate_file_signature(valid_pdf))
        
        # Invalid / Fake file
        fake_file = SimpleUploadedFile("fake.jpg", b"MALICIOUS_PAYLOAD_HERE", content_type="image/jpeg")
        self.assertFalse(validate_file_signature(fake_file))

    def test_pimpinan_cannot_delete_laporan(self):
        client = Client()
        client.login(username='pimpinan1', password='password123')
        
        # Try to delete
        response = client.get(reverse('laporan_hapus', args=[self.laporan.pk]))
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        # Verify Laporan still exists
        self.assertTrue(Laporan.objects.filter(pk=self.laporan.pk).exists())

    def test_pimpinan_cannot_delete_dokumentasi(self):
        client = Client()
        client.login(username='pimpinan1', password='password123')
        
        # Try to delete doc
        response = client.get(reverse('dokumentasi_hapus', args=[self.dokumentasi.pk]))
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        # Verify Dokumentasi still exists
        self.assertTrue(Dokumentasi.objects.filter(pk=self.dokumentasi.pk).exists())

    def test_pptk_created_kegiatan_is_diajukan_status(self):
        client = Client()
        client.login(username='pptk1', password='password123')
        
        # Create a new kegiatan as pptk
        response = client.post(reverse('kegiatan_tambah'), {
            'judul_kegiatan': 'Proyek Baru PPTK',
            'tahun': 2026,
            'latitude': -6.1234,
            'longitude': 106.1234
        })
        self.assertEqual(response.status_code, 302) # Redirect to list
        
        # Verify status is 'diajukan'
        kegiatan = Kegiatan.objects.get(judul_kegiatan='Proyek Baru PPTK')
        self.assertEqual(kegiatan.status, 'diajukan')

