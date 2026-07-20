import os
import sys
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

def compress_image(uploaded_file, max_width=1200, quality=75):
    """
    Mengompresi file gambar yang diunggah:
    - Mengonversi format ke JPEG (dan menangani transparency jika RGBA/LA).
    - Mengurangi lebar maksimal gambar ke 1200px (menjaga rasio aspek).
    - Menyimpan dengan kualitas 75% untuk menghemat penyimpanan.
    """
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    # Hanya kompresi jika berupa file gambar (.jpg, .jpeg, .png)
    if ext not in ['.jpg', '.jpeg', '.png']:
        return uploaded_file
        
    try:
        # Buka berkas gambar
        img = Image.open(uploaded_file)
        
        # Konversi RGBA/LA ke RGB agar bisa disimpan sebagai JPEG
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            # Gunakan alpha channel sebagai mask jika ada
            mask = img.split()[3] if len(img.split()) > 3 else None
            background.paste(img, mask=mask)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Ubah ukuran jika lebar gambar melebihi max_width
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * float(ratio))
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
        # Simpan ke memori buffer sebagai JPEG
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality)
        output.seek(0)
        
        # Buat nama file baru dengan ekstensi .jpg
        name_without_ext = os.path.splitext(uploaded_file.name)[0]
        new_filename = f"{name_without_ext}.jpg"
        
        # Buat objek InMemoryUploadedFile Django baru
        compressed_file = InMemoryUploadedFile(
            output,
            'FileField',
            new_filename,
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
        return compressed_file
    except Exception:
        # Jika kompresi gagal karena alasan apa pun, kembalikan berkas asli
        return uploaded_file


def validate_file_signature(uploaded_file):
    """
    Validates uploaded file by checking its magic bytes (file signature).
    Returns True if valid image (JPEG/PNG) or PDF, False otherwise.
    """
    try:
        # Read the first 8 bytes
        header = uploaded_file.read(8)
        # Seek back to the beginning so subsequent reads work correctly
        uploaded_file.seek(0)
        
        # Check signatures
        if header.startswith(b'\xff\xd8\xff'): # JPEG
            return True
        if header.startswith(b'\x89PNG\r\n\x1a\n'): # PNG
            return True
        if header.startswith(b'%PDF-'): # PDF
            return True
    except Exception:
        pass
        
    return False

