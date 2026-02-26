
from django.conf import settings
from simply_notes.views import create_admin
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create-admin/', create_admin),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)