from django.contrib import admin
from .models import Job, Application
from django.utils.html import format_html


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
    list_display = (
        'full_name',
        'email',
        'job',
        'applied_at',
        'view_resume',
    )

    search_fields = ('full_name', 'email')
    list_filter = ('applied_at',)

    @admin.display(description='Resume')
    def view_resume(self, obj):
        if obj.resume:
            return format_html(
                '<a href="{}" target="_blank">View Resume</a>',
                obj.resume.url
            )
        return "No resume"