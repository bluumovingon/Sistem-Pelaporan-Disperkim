from pelaporan.models import Notifikasi

def unread_notifications(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': Notifikasi.objects.filter(user=request.user, is_read=False).count(),
            'latest_unread_notifications': Notifikasi.objects.filter(user=request.user, is_read=False)[:5]
        }
    return {
        'unread_notifications_count': 0,
        'latest_unread_notifications': []
    }
