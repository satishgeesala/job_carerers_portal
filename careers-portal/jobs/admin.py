from django.contrib import admin
from .models import Job, Application


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'location', 'department',
        'job_type', 'closing_date', 'is_active'
    )
    list_filter = ('is_active', 'job_type', 'department')
    search_fields = ('title', 'location', 'department')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'job', 'applied_at')
    search_fields = ('full_name', 'email')
    list_filter = ('applied_at',)