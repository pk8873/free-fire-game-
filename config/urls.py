from django.contrib import admin
from django.urls import path
from core.views import home, manifest, service_worker

urlpatterns = [path('admin/', admin.site.urls), path('', home, name='home'), path('manifest.webmanifest', manifest, name='manifest'), path('service-worker.js', service_worker, name='service-worker')]
