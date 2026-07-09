from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.db.models import Q, Count
from django.utils import timezone
from django.urls import reverse
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from pelaporan.models import User, Kegiatan, Laporan, Dokumentasi, RiwayatStatus, Notifikasi
from pelaporan.forms import LaporanForm, KegiatanForm, UserForm
from pelaporan.decorators import role_required

# --- Auth & Redirects ---

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(username=u, password=p)
        if user is not None:
            if user.status_aktif:
                login(request, user)
                messages.success(request, f"Selamat datang kembali, {user.first_name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Akun Anda dinonaktifkan. Silakan hubungi Super Admin.")
        else:
            messages.error(request, "Username atau password salah.")
            
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Anda telah berhasil keluar dari sistem.")
    return redirect('login')


# --- Dashboard ---

@login_required
def dashboard_view(request):
    user = request.user
    
    if user.role == 'pptk':
        # Dashboard PPTK
        laporans = Laporan.objects.filter(pptk=user)
        
        stats = {
            'total': laporans.count(),
            'draft': laporans.filter(status='draft').count(),
            'diajukan': laporans.filter(status='diajukan').count(),
            'terverifikasi': laporans.filter(status='terverifikasi').count(),
            'perlu_revisi': laporans.filter(status='perlu_revisi').count(),
        }
        
        recent_laporans = laporans.order_by('-updated_at')[:5]
        
        context = {
            'stats': stats,
            'recent_laporans': recent_laporans,
        }
        return render(request, 'dashboard/pptk.html', context)
        
    else:
        # Dashboard Admin / Pimpinan / Super Admin
        laporans = Laporan.objects.all()
        
        stats = {
            'total': laporans.count(),
            'diajukan': laporans.filter(status='diajukan').count(),
            'terverifikasi': laporans.filter(status='terverifikasi').count(),
            'perlu_revisi': laporans.filter(status='perlu_revisi').count(),
        }
        
        # Reports waiting verification (only for Admin / Super Admin)
        pending_reports = laporans.filter(status='diajukan').order_by('-updated_at')
        
        # Chart Data
        # 1. Reports by status
        status_chart_data = list(laporans.values('status').annotate(count=Count('id')))
        # 2. Reports by Month
        month_chart_data = list(laporans.values('bulan_laporan').annotate(count=Count('id')))
        # 3. Reports by PPTK
        pptk_chart_data = list(laporans.values('pptk__first_name', 'pptk__last_name').annotate(count=Count('id')))
        
        context = {
            'stats': stats,
            'pending_reports': pending_reports[:10],
            'status_chart_data': status_chart_data,
            'month_chart_data': month_chart_data,
            'pptk_chart_data': pptk_chart_data,
        }
        return render(request, 'dashboard/admin.html', context)


# --- Laporan CRUD ---

@login_required
def laporan_list_view(request):
    user = request.user
    
    # Base query based on roles
    if user.role == 'pptk':
        laporans = Laporan.objects.filter(pptk=user)
    else:
        laporans = Laporan.objects.all()
        
    # Apply Filters
    q_status = request.GET.get('status')
    q_bulan = request.GET.get('bulan')
    q_kegiatan = request.GET.get('kegiatan')
    q_pptk = request.GET.get('pptk')
    q_search = request.GET.get('search')
    
    if q_status:
        laporans = laporans.filter(status=q_status)
    if q_bulan:
        laporans = laporans.filter(bulan_laporan=q_bulan)
    if q_kegiatan:
        laporans = laporans.filter(kegiatan_id=q_kegiatan)
    if q_pptk and user.role != 'pptk':
        laporans = laporans.filter(pptk_id=q_pptk)
    if q_search:
        laporans = laporans.filter(
            Q(kegiatan__judul_kegiatan__icontains=q_search) | 
            Q(tahapan_pelaksanaan__icontains=q_search) | 
            Q(kendala__icontains=q_search)
        )
        
    # Get metadata for filter inputs
    if user.role == 'pptk':
        all_kegiatans = Kegiatan.objects.filter(pptk=user)
    else:
        all_kegiatans = Kegiatan.objects.all()
    all_pptk = User.objects.filter(role='pptk')
    all_bulans = [b[0] for b in Laporan.BULAN_CHOICES]
    all_statuses = Laporan.STATUS_CHOICES
    
    context = {
        'laporans': laporans,
        'all_kegiatans': all_kegiatans,
        'all_pptk': all_pptk,
        'all_bulans': all_bulans,
        'all_statuses': all_statuses,
        'filters': {
            'status': q_status or '',
            'bulan': q_bulan or '',
            'kegiatan': q_kegiatan or '',
            'pptk': q_pptk or '',
            'search': q_search or '',
        }
    }
    return render(request, 'laporan/list.html', context)


@login_required
@role_required('pptk')
def laporan_buat_view(request):
    if request.method == 'POST':
        form = LaporanForm(request.POST)
        form.fields['kegiatan'].queryset = Kegiatan.objects.filter(pptk=request.user)
        if form.is_valid():
            laporan = form.save(commit=False)
            laporan.pptk = request.user
            
            # Check action (draft or submit)
            action = request.POST.get('action')
            if action == 'diajukan':
                laporan.status = 'diajukan'
            else:
                laporan.status = 'draft'
                
            laporan.save()
            
            # Save historical log
            RiwayatStatus.objects.create(
                laporan=laporan,
                status_lama='draft', # dummy initial status
                status_baru=laporan.status,
                diubah_oleh=request.user,
                catatan='Laporan dibuat pertama kali.'
            )
            
            # Save files
            files = request.FILES.getlist('files')
            file_descriptions = request.POST.getlist('file_descriptions')
            for i, f in enumerate(files):
                desc = file_descriptions[i] if i < len(file_descriptions) else ''
                Dokumentasi.objects.create(
                    laporan=laporan,
                    file=f,
                    keterangan=desc
                )
                
            # If submitted directly, notify admins
            if action == 'diajukan':
                admins = User.objects.filter(role__in=['admin', 'super_admin'])
                for admin in admins:
                    Notifikasi.objects.create(
                        user=admin,
                        judul="Laporan Baru Diajukan",
                        pesan=f"Laporan kegiatan '{laporan.kegiatan.judul_kegiatan}' bulan {laporan.bulan_laporan} telah diajukan oleh {request.user.first_name} {request.user.last_name}.",
                        laporan=laporan
                    )
                    
            messages.success(request, f"Laporan berhasil disimpan sebagai {laporan.get_status_display()}.")
            return redirect('laporan_list')
    else:
        form = LaporanForm()
        form.fields['kegiatan'].queryset = Kegiatan.objects.filter(pptk=request.user)
        
    return render(request, 'laporan/form.html', {'form': form, 'is_new': True})


@login_required
def laporan_detail_view(request, pk):
    laporan = get_object_or_404(Laporan, pk=pk)
    
    # Authorization check
    if request.user.role == 'pptk' and laporan.pptk != request.user:
        messages.error(request, "Anda tidak diperbolehkan melihat laporan ini.")
        return redirect('dashboard')
        
    riwayats = laporan.riwayat_status.all().order_by('-created_at')
    dokumentasis = laporan.dokumentasi.all()
    
    context = {
        'laporan': laporan,
        'riwayats': riwayats,
        'dokumentasis': dokumentasis,
    }
    return render(request, 'laporan/detail.html', context)


@login_required
@role_required('pptk')
def laporan_edit_view(request, pk):
    laporan = get_object_or_404(Laporan, pk=pk)
    
    # Ownership & status constraint checks
    if laporan.pptk != request.user:
        messages.error(request, "Anda hanya bisa mengedit laporan milik sendiri.")
        return redirect('dashboard')
        
    if not (laporan.status == 'draft' or laporan.status == 'perlu_revisi'):
        messages.error(request, "Laporan yang sudah diajukan atau diverifikasi tidak bisa diedit.")
        return redirect('laporan_detail', pk=laporan.pk)
        
    if request.method == 'POST':
        form = LaporanForm(request.POST, instance=laporan)
        form.fields['kegiatan'].queryset = Kegiatan.objects.filter(pptk=request.user)
        if form.is_valid():
            original_status = laporan.status
            laporan = form.save(commit=False)
            laporan.pptk = request.user
            
            # Check action
            action = request.POST.get('action')
            if action == 'diajukan':
                laporan.status = 'diajukan'
                
            laporan.save()
            
            # Save status log if status changed
            if original_status != laporan.status:
                RiwayatStatus.objects.create(
                    laporan=laporan,
                    status_lama=original_status,
                    status_baru=laporan.status,
                    diubah_oleh=request.user,
                    catatan='Laporan diajukan kembali setelah diedit/revisi.'
                )
                
                # Notify admins
                admins = User.objects.filter(role__in=['admin', 'super_admin'])
                for admin in admins:
                    Notifikasi.objects.create(
                        user=admin,
                        judul="Laporan Pengajuan Ulang",
                        pesan=f"Laporan kegiatan '{laporan.kegiatan.judul_kegiatan}' bulan {laporan.bulan_laporan} diajukan kembali oleh {request.user.first_name} {request.user.last_name}.",
                        laporan=laporan
                    )
            
            # Save files
            files = request.FILES.getlist('files')
            file_descriptions = request.POST.getlist('file_descriptions')
            for i, f in enumerate(files):
                desc = file_descriptions[i] if i < len(file_descriptions) else ''
                Dokumentasi.objects.create(
                    laporan=laporan,
                    file=f,
                    keterangan=desc
                )
                
            messages.success(request, f"Laporan berhasil diperbarui.")
            return redirect('laporan_detail', pk=laporan.pk)
    else:
        form = LaporanForm(instance=laporan)
        form.fields['kegiatan'].queryset = Kegiatan.objects.filter(pptk=request.user)
        
    dokumentasis = laporan.dokumentasi.all()
    context = {
        'form': form,
        'laporan': laporan,
        'dokumentasis': dokumentasis,
        'is_new': False
    }
    return render(request, 'laporan/form.html', context)


@login_required
@role_required('admin', 'super_admin')
def laporan_verifikasi_view(request, pk):
    laporan = get_object_or_404(Laporan, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        catatan = request.POST.get('catatan_revisi', '')
        
        status_lama = laporan.status
        
        if action == 'approve':
            laporan.status = 'terverifikasi'
            laporan.catatan_revisi = ''
            laporan.save()
            
            # Histori
            RiwayatStatus.objects.create(
                laporan=laporan,
                status_lama=status_lama,
                status_baru='terverifikasi',
                diubah_oleh=request.user,
                catatan='Laporan disetujui dan diverifikasi.'
            )
            
            # Notify pptk
            Notifikasi.objects.create(
                user=laporan.pptk,
                judul="Laporan Disetujui",
                pesan=f"Laporan kegiatan '{laporan.kegiatan.judul_kegiatan}' untuk bulan {laporan.bulan_laporan} telah disetujui oleh Admin.",
                laporan=laporan
            )
            
            messages.success(request, "Laporan berhasil diverifikasi/disetujui.")
            
        elif action == 'reject':
            if not catatan:
                messages.error(request, "Catatan alasan revisi harus diisi.")
                return redirect('laporan_detail', pk=laporan.pk)
                
            laporan.status = 'perlu_revisi'
            laporan.catatan_revisi = catatan
            laporan.save()
            
            # Histori
            RiwayatStatus.objects.create(
                laporan=laporan,
                status_lama=status_lama,
                status_baru='perlu_revisi',
                diubah_oleh=request.user,
                catatan=f"Laporan ditolak / perlu revisi. Catatan: {catatan}"
            )
            
            # Notify pptk
            Notifikasi.objects.create(
                user=laporan.pptk,
                judul="Laporan Butuh Revisi",
                pesan=f"Laporan kegiatan '{laporan.kegiatan.judul_kegiatan}' bulan {laporan.bulan_laporan} ditolak/butuh revisi. Catatan: {catatan}",
                laporan=laporan
            )
            
            messages.warning(request, "Laporan ditolak dan dikembalikan ke PPTK untuk direvisi.")
            
    return redirect('laporan_detail', pk=laporan.pk)


@login_required
def laporan_hapus_view(request, pk):
    laporan = get_object_or_404(Laporan, pk=pk)
    
    # Auth constraint
    if request.user.role == 'pptk' and laporan.pptk != request.user:
        messages.error(request, "Anda tidak diizinkan menghapus laporan ini.")
        return redirect('dashboard')
        
    if request.user.role == 'pptk' and laporan.status not in ['draft', 'perlu_revisi']:
        messages.error(request, "Anda hanya bisa menghapus laporan berstatus Draft atau Perlu Revisi.")
        return redirect('laporan_detail', pk=laporan.pk)
        
    # Delete file fields from disk
    docs = laporan.dokumentasi.all()
    for doc in docs:
        if doc.file:
            try:
                doc.file.delete(save=False)
            except Exception:
                pass
                
    laporan.delete()
    messages.success(request, "Laporan berhasil dihapus.")
    return redirect('laporan_list')


@login_required
def dokumentasi_hapus_view(request, pk):
    doc = get_object_or_404(Dokumentasi, pk=pk)
    laporan = doc.laporan
    
    # Auth constraint
    if request.user.role == 'pptk' and laporan.pptk != request.user:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('dashboard')))
        
    if request.user.role == 'pptk' and laporan.status not in ['draft', 'perlu_revisi']:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('dashboard')))
        
    # Delete from disk
    if doc.file:
        try:
            doc.file.delete(save=False)
        except Exception:
            pass
            
    doc.delete()
    messages.success(request, "File dokumentasi berhasil dihapus.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('laporan_edit', args=[laporan.pk])))


# --- Rekap & Exports ---

@login_required
@role_required('admin', 'pimpinan', 'super_admin')
def rekap_view(request):
    # Apply Filters
    q_bulan = request.GET.get('bulan')
    q_kegiatan = request.GET.get('kegiatan')
    q_pptk = request.GET.get('pptk')
    
    # We only show terverifikasi reports in the recap sheet
    laporans = Laporan.objects.filter(status='terverifikasi')
    
    if q_bulan:
        laporans = laporans.filter(bulan_laporan=q_bulan)
    if q_kegiatan:
        laporans = laporans.filter(kegiatan_id=q_kegiatan)
    if q_pptk:
        laporans = laporans.filter(pptk_id=q_pptk)
        
    all_kegiatans = Kegiatan.objects.all()
    all_pptk = User.objects.filter(role='pptk')
    all_bulans = [b[0] for b in Laporan.BULAN_CHOICES]
    
    context = {
        'laporans': laporans,
        'all_kegiatans': all_kegiatans,
        'all_pptk': all_pptk,
        'all_bulans': all_bulans,
        'filters': {
            'bulan': q_bulan or '',
            'kegiatan': q_kegiatan or '',
            'pptk': q_pptk or '',
        }
    }
    return render(request, 'rekap/rekap.html', context)


@login_required
@role_required('admin', 'pimpinan', 'super_admin')
def rekap_excel_view(request):
    q_bulan = request.GET.get('bulan')
    q_kegiatan = request.GET.get('kegiatan')
    q_pptk = request.GET.get('pptk')
    
    # Filter reports
    laporans = Laporan.objects.filter(status='terverifikasi')
    if q_bulan:
        laporans = laporans.filter(bulan_laporan=q_bulan)
    if q_kegiatan:
        laporans = laporans.filter(kegiatan_id=q_kegiatan)
    if q_pptk:
        laporans = laporans.filter(pptk_id=q_pptk)
        
    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rekap Laporan"
    
    # Grid lines visible
    ws.views.sheetView[0].showGridLines = True
    
    # Title Block
    ws.merge_cells("A1:H1")
    ws["A1"] = "REKAPITULASI LAPORAN KEGIATAN PENGAWASAN LAPANGAN"
    ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="000000")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    
    ws.merge_cells("A2:H2")
    ws["A2"] = "DINAS PERUMAHAN DAN PERMUKIMAN (DISPERKIM)"
    ws["A2"].font = Font(name="Calibri", size=12, bold=True)
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    
    ws.merge_cells("A3:H3")
    filter_desc = "Semua Laporan Terverifikasi"
    if q_bulan:
        filter_desc += f" | Bulan: {q_bulan}"
    ws["A3"] = filter_desc
    ws["A3"].font = Font(name="Calibri", size=10, italic=True)
    ws["A3"].alignment = Alignment(horizontal="center", vertical="center")
    
    # Row Heights
    ws.row_dimensions[1].height = 25
    ws.row_dimensions[2].height = 20
    ws.row_dimensions[3].height = 15
    ws.row_dimensions[5].height = 26
    
    # Headers
    headers = [
        "No", 
        "Nama PPTK", 
        "Jabatan PPTK", 
        "Judul Kegiatan", 
        "Bulan Laporan", 
        "Tahapan Pelaksanaan", 
        "Kendala", 
        "Status"
    ]
    
    # Styling variables
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    # Write headers (row 5)
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
        
    # Write data rows
    current_row = 6
    for idx, lap in enumerate(laporans, 1):
        ws.row_dimensions[current_row].height = 35  # tall data rows for text wrapping
        
        c1 = ws.cell(row=current_row, column=1, value=idx)
        c1.alignment = center_align
        
        c2 = ws.cell(row=current_row, column=2, value=f"{lap.pptk.first_name} {lap.pptk.last_name}")
        c2.alignment = left_align
        
        c3 = ws.cell(row=current_row, column=3, value=lap.pptk.jabatan)
        c3.alignment = left_align
        
        c4 = ws.cell(row=current_row, column=4, value=lap.kegiatan.judul_kegiatan)
        c4.alignment = left_align
        
        c5 = ws.cell(row=current_row, column=5, value=lap.bulan_laporan)
        c5.alignment = center_align
        
        c6 = ws.cell(row=current_row, column=6, value=lap.tahapan_pelaksanaan)
        c6.alignment = left_align
        
        c7 = ws.cell(row=current_row, column=7, value=lap.kendala or "-")
        c7.alignment = left_align
        
        c8 = ws.cell(row=current_row, column=8, value=lap.get_status_display())
        c8.alignment = center_align
        
        # Apply borders and fonts to data cells
        for col_idx in range(1, 9):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = Font(name="Calibri", size=10)
            cell.border = thin_border
            
        current_row += 1
        
    # Adjust column widths
    column_widths = {
        'A': 5,   # No
        'B': 25,  # Nama PPTK
        'C': 25,  # Jabatan PPTK
        'D': 35,  # Judul Kegiatan
        'E': 15,  # Bulan
        'F': 45,  # Tahapan
        'G': 30,  # Kendala
        'H': 15,  # Status
    }
    
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width
        
    # Build response
    filename = f"rekap_sipawas_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


@login_required
def rekap_pdf_view(request, pk):
    laporan = get_object_or_404(Laporan, pk=pk)
    
    # Auth constraint
    if request.user.role == 'pptk' and laporan.pptk != request.user:
        messages.error(request, "Anda tidak diperbolehkan mengakses cetak laporan ini.")
        return redirect('dashboard')
        
    dokumentasis = laporan.dokumentasi.all()
    riwayats = laporan.riwayat_status.all().order_by('created_at')
    
    context = {
        'laporan': laporan,
        'dokumentasis': dokumentasis,
        'riwayats': riwayats,
        'current_date': timezone.now()
    }
    return render(request, 'rekap/pdf_report.html', context)


# --- Master Kegiatan ---

@login_required
@role_required('admin', 'super_admin', 'pptk')
def kegiatan_list_view(request):
    user = request.user
    if user.role == 'pptk':
        kegiatans = Kegiatan.objects.filter(pptk=user)
    else:
        kegiatans = Kegiatan.objects.all()
    return render(request, 'master/kegiatan_list.html', {'kegiatans': kegiatans})


@login_required
@role_required('admin', 'super_admin', 'pptk')
def kegiatan_tambah_view(request):
    if request.method == 'POST':
        form = KegiatanForm(request.POST)
        if request.user.role == 'pptk':
            form.fields['pptk'].required = False
        if form.is_valid():
            kegiatan = form.save(commit=False)
            if request.user.role == 'pptk':
                kegiatan.pptk = request.user
            kegiatan.save()
            messages.success(request, "Master data Kegiatan berhasil ditambahkan.")
            return redirect('kegiatan_list')
    else:
        form = KegiatanForm()
        if request.user.role == 'pptk':
            form.fields['pptk'].required = False
    return render(request, 'master/kegiatan_form.html', {'form': form, 'is_new': True})


@login_required
@role_required('admin', 'super_admin', 'pptk')
def kegiatan_edit_view(request, pk):
    kegiatan = get_object_or_404(Kegiatan, pk=pk)
    if request.user.role == 'pptk' and kegiatan.pptk != request.user:
        messages.error(request, "Anda hanya dapat mengubah kegiatan milik sendiri.")
        return redirect('kegiatan_list')
        
    if request.method == 'POST':
        form = KegiatanForm(request.POST, instance=kegiatan)
        if request.user.role == 'pptk':
            form.fields['pptk'].required = False
        if form.is_valid():
            kegiatan = form.save(commit=False)
            if request.user.role == 'pptk':
                kegiatan.pptk = request.user
            kegiatan.save()
            messages.success(request, "Master data Kegiatan berhasil diperbarui.")
            return redirect('kegiatan_list')
    else:
        form = KegiatanForm(instance=kegiatan)
        if request.user.role == 'pptk':
            form.fields['pptk'].required = False
    return render(request, 'master/kegiatan_form.html', {'form': form, 'is_new': False, 'kegiatan': kegiatan})


@login_required
@role_required('admin', 'super_admin', 'pptk')
def kegiatan_hapus_view(request, pk):
    kegiatan = get_object_or_404(Kegiatan, pk=pk)
    if request.user.role == 'pptk' and kegiatan.pptk != request.user:
        messages.error(request, "Anda hanya dapat menghapus kegiatan milik sendiri.")
        return redirect('kegiatan_list')
        
    if kegiatan.laporan.exists():
        messages.error(request, "Tidak dapat menghapus Kegiatan karena masih terhubung dengan laporan aktif.")
    else:
        kegiatan.delete()
        messages.success(request, "Master data Kegiatan berhasil dihapus.")
    return redirect('kegiatan_list')


# --- Master Pengguna (Super Admin) ---

@login_required
@role_required('super_admin')
def pengguna_list_view(request):
    penggunas = User.objects.all()
    return render(request, 'master/pengguna_list.html', {'penggunas': penggunas})


@login_required
@role_required('super_admin')
def pengguna_tambah_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = user.role in ['admin', 'super_admin']
            user.is_superuser = user.role == 'super_admin'
            user.save()
            messages.success(request, f"Pengguna '{user.username}' berhasil ditambahkan.")
            return redirect('pengguna_list')
    else:
        form = UserForm()
    return render(request, 'master/pengguna_form.html', {'form': form, 'is_new': True})


@login_required
@role_required('super_admin')
def pengguna_edit_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = user.role in ['admin', 'super_admin']
            user.is_superuser = user.role == 'super_admin'
            user.save()
            messages.success(request, f"Pengguna '{user.username}' berhasil diperbarui.")
            return redirect('pengguna_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'master/pengguna_form.html', {'form': form, 'is_new': False, 'target_user': user})


@login_required
@role_required('super_admin')
def pengguna_hapus_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "Anda tidak dapat menghapus akun Anda sendiri yang sedang aktif.")
    else:
        username = user.username
        user.delete()
        messages.success(request, f"Pengguna '{username}' berhasil dihapus.")
    return redirect('pengguna_list')


# --- Notifikasi ---

@login_required
def notifikasi_list_view(request):
    notifs = Notifikasi.objects.filter(user=request.user)
    return render(request, 'notifikasi/list.html', {'notifs': notifs})


@login_required
def notifikasi_baca_view(request, pk):
    notif = get_object_or_404(Notifikasi, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    if notif.laporan:
        return redirect('laporan_detail', pk=notif.laporan.pk)
    return redirect('notifikasi_list')


@login_required
def notifikasi_baca_semua_view(request):
    Notifikasi.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Semua notifikasi telah ditandai sebagai dibaca.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('dashboard')))
