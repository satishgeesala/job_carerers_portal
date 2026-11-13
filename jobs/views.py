
import os
import time
import requests
import cloudinary.utils

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.admin.views.decorators import staff_member_required

from .models import Job, Application


def home(request):
    jobs = Job.objects.filter(
        is_active=True,
        closing_date__gte=timezone.localdate()
    ).order_by('-created_at')[:5]

    return render(request, 'jobs/home.html', {
        'jobs': jobs
    })


def job_list(request):
    jobs = Job.objects.filter(
        is_active=True,
        closing_date__gte=timezone.localdate()
    ).order_by('-created_at')

    search_query = request.GET.get('q', '')

    if search_query:
        from django.db.models import Q
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    location = request.GET.get('location', '')
    if location:
        jobs = jobs.filter(location__icontains=location)

    department = request.GET.get('department', '')
    if department:
        jobs = jobs.filter(department__icontains=department)

    job_type = request.GET.get('job_type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    paginator = Paginator(jobs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'location': location,
        'department': department,
        'job_type': job_type,
    })


def job_detail(request, slug):
    job = get_object_or_404(
        Job,
        slug=slug,
        is_active=True,
        closing_date__gte=timezone.localdate()
    )

    return render(request, 'jobs/job_detail.html', {
        'job': job
    })


def apply_job(request, slug):
    job = get_object_or_404(
        Job,
        slug=slug,
        is_active=True,
        closing_date__gte=timezone.localdate()
    )

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        resume = request.FILES.get('resume')
        cover_letter = request.POST.get('cover_letter')

        # Validate required fields
        if not full_name or not email or not phone:
            return render(request, 'jobs/apply_job.html', {
                'job': job,
                'error': 'Please fill in all required fields.'
            })

        # Prevent duplicate applications
        if Application.objects.filter(
            job=job,
            email=email
        ).exists():
            return render(request, 'jobs/apply_job.html', {
                'job': job,
                'error': 'You have already applied for this job.'
            })

        # Validate resume
        if not resume:
            return render(request, 'jobs/apply_job.html', {
                'job': job,
                'error': 'Please upload your resume.'
            })

        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_extension = os.path.splitext(resume.name)[1].lower()

        if file_extension not in allowed_extensions:
            return render(request, 'jobs/apply_job.html', {
                'job': job,
                'error': 'Only PDF, DOC and DOCX files are allowed.'
            })

        if resume.size > 5 * 1024 * 1024:
            return render(request, 'jobs/apply_job.html', {
                'job': job,
                'error': 'Resume size must be below 5 MB.'
            })

        # Save application
        Application.objects.create(
            job=job,
            full_name=full_name,
            email=email,
            phone=phone,
            resume=resume,
            cover_letter=cover_letter
        )

        return redirect('thank_you')

    return render(request, 'jobs/apply_job.html', {
        'job': job
    })


def thank_you(request):
    return render(request, 'jobs/thank_you.html')


@staff_member_required
def download_resume(request, application_id):
    application = get_object_or_404(
        Application,
        id=application_id
    )

    # Check application viewing permission
    if not request.user.has_perm('jobs.view_application'):
        raise PermissionDenied

    if not application.resume:
        return redirect('admin:jobs_application_changelist')

    public_id = application.resume.name

    # Generate temporary authenticated Cloudinary URL
    resume_url = cloudinary.utils.private_download_url(
        public_id,
        None,
        resource_type='raw',
        type='authenticated',
        expires_at=int(time.time()) + 300,
        attachment=False,
    )

    try:
        # Retrieve PDF from Cloudinary
        cloudinary_response = requests.get(
            resume_url,
            timeout=30
        )
        cloudinary_response.raise_for_status()

        pdf_content = cloudinary_response.content
        cloudinary_response.close()

        # Display PDF directly in browser
        response = HttpResponse(
            pdf_content,
            content_type='application/pdf'
        )

        response['Content-Disposition'] = 'inline; filename="resume.pdf"'
        response['X-Content-Type-Options'] = 'nosniff'

        return response

    except requests.RequestException:
        return HttpResponse(
            'Unable to retrieve the resume. Please try again.',
            status=502
        )
