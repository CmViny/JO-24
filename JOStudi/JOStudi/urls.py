from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from JOStudi.settings import BASE_DIR
import os

urlpatterns = [
    path('admin/', admin.site.urls),

    # Apps
    path('', include('store.urls')),
    path('accounts/', include('accounts.urls')),
    path('offers/', include('offers.urls')),
    path('cart/', include('cart.urls')),
    path('reservations/', include('reservations.urls')),
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(BASE_DIR, 'static'))