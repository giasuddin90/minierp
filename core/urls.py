from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from . import views
from . import admin_views

def redirect_to_dashboard(request):
    return redirect('/dashboard/')

urlpatterns = [
    path('', redirect_to_dashboard, name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),
    path('accounting/', include('accounting.urls')),
    path('reports/', include('reports.urls')),
    path('customers/', include('customers.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('stock/', include('stock.urls')),
    path('sales/', include('sales.urls')),
    path('purchases/', include('purchases.urls')),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
