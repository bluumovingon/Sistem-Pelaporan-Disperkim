from django import forms
from pelaporan.models import User, Kegiatan, Laporan, Dokumentasi

class LaporanForm(forms.ModelForm):
    class Meta:
        model = Laporan
        fields = ['kegiatan', 'bulan_laporan', 'tahapan_pelaksanaan', 'kendala']
        widgets = {
            'kegiatan': forms.Select(attrs={'class': 'form-select select2-enable', 'placeholder': 'Pilih Kegiatan'}),
            'bulan_laporan': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Pilih Bulan'}),
            'tahapan_pelaksanaan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Jelaskan progres/tahapan pelaksanaan kegiatan...'}),
            'kendala': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Sebutkan kendala yang dihadapi (bila ada)...'}),
        }


class KegiatanForm(forms.ModelForm):
    class Meta:
        model = Kegiatan
        fields = ['judul_kegiatan', 'pptk', 'tahun']
        widgets = {
            'judul_kegiatan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama/Judul Kegiatan'}),
            'pptk': forms.Select(attrs={'class': 'form-select'}),
            'tahun': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pptk'].queryset = User.objects.filter(role='pptk')
        self.fields['pptk'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} ({obj.jabatan})"


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        required=False,
        help_text="Kosongkan jika tidak ingin mengubah password saat edit."
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'jabatan', 'unit_kerja', 'status_aktif']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'jabatan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Kasi Perumahan'}),
            'unit_kerja': forms.TextInput(attrs={'class': 'form-control'}),
            'status_aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
