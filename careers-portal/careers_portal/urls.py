from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Avalanche High-Tech Enterprises Careers Portal Administration"
admin.site.site_title = "Careers Portal Admin"
admin.site.index_title = "Welcome to Careers Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),
]
