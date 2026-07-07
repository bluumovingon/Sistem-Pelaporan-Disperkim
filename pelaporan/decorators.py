from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages

def role_required(*allowed_roles):
    """
    Decorator to restrict access to views based on user roles.
    Allowed roles: 'super_admin', 'admin', 'pengawas', 'pimpinan'.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Allow super_admin to access everything
            if request.user.role == 'super_admin' or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # If role is not allowed, show message and redirect to dashboard
            messages.error(request, "Anda tidak memiliki hak akses untuk halaman tersebut.")
            return redirect('dashboard')
            
        return _wrapped_view
    return decorator
