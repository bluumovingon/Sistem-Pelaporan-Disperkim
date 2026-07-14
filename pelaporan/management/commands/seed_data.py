from django.core.management.base import BaseCommand
from pelaporan.models import User, Kegiatan
import os

class Command(BaseCommand):
    help = 'Seeds initial data for SIPAWAS project'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding initial data...')

        # 1. Create Users
        self.stdout.write('Creating users...')
        
        # Super Admin
        if not User.objects.filter(username='superadmin').exists():
            superadmin = User.objects.create_superuser(
                username='superadmin',
                email='superadmin@disperkim.go.id',
                password='admin123',
                first_name='Super',
                last_name='Admin',
                role='super_admin',
                unit_kerja='Sekretariat'
            )
            self.stdout.write(self.style.SUCCESS('Superadmin user created (superadmin / admin123)'))
        else:
            self.stdout.write('Superadmin user already exists.')

        # Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                email='admin@disperkim.go.id',
                password='admin123',
                first_name='Rian',
                last_name='Hidayat',
                role='admin',
                unit_kerja='Bidang Perumahan dan Permukiman'
            )
            self.stdout.write(self.style.SUCCESS('Admin user created (admin / admin123)'))
        else:
            self.stdout.write('Admin user already exists.')

        # PPTK 1 User
        pptk1 = None
        if not User.objects.filter(username='pptk1').exists():
            pptk1 = User.objects.create_user(
                username='pptk1',
                email='ahmad@disperkim.go.id',
                password='pengawas123',
                first_name='Ahmad',
                last_name='Subarjo, S.T.',
                role='pptk',
                jabatan='Kasi Perumahan Rakyat',
                unit_kerja='Bidang Perumahan'
            )
            self.stdout.write(self.style.SUCCESS('PPTK 1 created (pptk1 / pengawas123)'))
        else:
            pptk1 = User.objects.get(username='pptk1')
            self.stdout.write('PPTK 1 already exists.')

        # PPTK 2 User
        pptk2 = None
        if not User.objects.filter(username='pptk2').exists():
            pptk2 = User.objects.create_user(
                username='pptk2',
                email='rina@disperkim.go.id',
                password='pengawas123',
                first_name='Rina',
                last_name='Wijayanti, M.T.',
                role='pptk',
                jabatan='Kasi Permukiman Kumuh',
                unit_kerja='Bidang Permukiman'
            )
            self.stdout.write(self.style.SUCCESS('PPTK 2 created (pptk2 / pengawas123)'))
        else:
            pptk2 = User.objects.get(username='pptk2')
            self.stdout.write('PPTK 2 already exists.')

        # Pimpinan
        if not User.objects.filter(username='pimpinan').exists():
            pimpinan = User.objects.create_user(
                username='pimpinan',
                email='kadin@disperkim.go.id',
                password='pimpinan123',
                first_name='Drs. Heru',
                last_name='Prasetyo, M.Si',
                role='pimpinan',
                unit_kerja='Kepala Dinas DISPERKIM'
            )
            self.stdout.write(self.style.SUCCESS('Pimpinan created (pimpinan / pimpinan123)'))
        else:
            self.stdout.write('Pimpinan already exists.')

        # 2. Create Kegiatan (Proyek)
        self.stdout.write('Creating Kegiatan...')
        keg1, created = Kegiatan.objects.get_or_create(
            judul_kegiatan='Pembangunan Rumah Swadaya Kecamatan A',
            pptk=pptk1,
            defaults={'tahun': 2026}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Kegiatan 1 created'))

        keg2, created = Kegiatan.objects.get_or_create(
            judul_kegiatan='Peningkatan Kualitas Jalan Lingkungan Kelurahan B',
            pptk=pptk2,
            defaults={'tahun': 2026}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Kegiatan 2 created'))

        keg3, created = Kegiatan.objects.get_or_create(
            judul_kegiatan='Pembangunan Drainase Lingkungan RT 05/RW 02 Kelurahan C',
            pptk=pptk2,
            defaults={'tahun': 2026}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Kegiatan 3 created'))

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
