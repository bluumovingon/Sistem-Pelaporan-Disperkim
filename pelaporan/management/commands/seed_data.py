from django.core.management.base import BaseCommand
from pelaporan.models import User, PPTK, Kegiatan
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

        # Pengawas 1
        if not User.objects.filter(username='pengawas1').exists():
            pengawas1 = User.objects.create_user(
                username='pengawas1',
                email='budi@disperkim.go.id',
                password='pengawas123',
                first_name='Budi',
                last_name='Santoso',
                role='pengawas',
                unit_kerja='Pengawas Bidang Perumahan'
            )
            self.stdout.write(self.style.SUCCESS('Pengawas 1 created (pengawas1 / pengawas123)'))
        else:
            self.stdout.write('Pengawas 1 already exists.')

        # Pengawas 2
        if not User.objects.filter(username='pengawas2').exists():
            pengawas2 = User.objects.create_user(
                username='pengawas2',
                email='siti@disperkim.go.id',
                password='pengawas123',
                first_name='Siti',
                last_name='Aminah',
                role='pengawas',
                unit_kerja='Pengawas Bidang Permukiman'
            )
            self.stdout.write(self.style.SUCCESS('Pengawas 2 created (pengawas2 / pengawas123)'))
        else:
            self.stdout.write('Pengawas 2 already exists.')

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

        # 2. Create PPTK
        self.stdout.write('Creating PPTK...')
        pptk1, created = PPTK.objects.get_or_create(
            nama='Ahmad Subarjo, S.T.',
            defaults={'jabatan': 'Kasi Perumahan Rakyat', 'unit_kerja': 'Bidang Perumahan'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('PPTK 1 created'))

        pptk2, created = PPTK.objects.get_or_create(
            nama='Rina Wijayanti, M.T.',
            defaults={'jabatan': 'Kasi Permukiman Kumuh', 'unit_kerja': 'Bidang Permukiman'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('PPTK 2 created'))

        # 3. Create Kegiatan
        self.stdout.write('Creating Kegiatan...')
        keg1, created = Kegiatan.objects.get_or_create(
            judul_kegiatan='Pembangunan Rumah Swadaya Kecamatan A',
            pptk=pptk1,
            tahun=2026
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Kegiatan 1 created'))

        keg2, created = Kegiatan.objects.get_or_create(
            judul_kegiatan='Peningkatan Kualitas Jalan Lingkungan Kelurahan B',
            pptk=pptk2,
            tahun=2026
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Kegiatan 2 created'))

        keg3, created = Kegiatan.objects.get_or_create(
            judul_kegiatan='Pembangunan Drainase Lingkungan RT 05/RW 02 Kelurahan C',
            pptk=pptk2,
            tahun=2026
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Kegiatan 3 created'))

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
