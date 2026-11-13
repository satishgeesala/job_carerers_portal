
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<slug:slug>/', views.job_detail, name='job_detail'),
    path('jobs/<slug:slug>/apply/', views.apply_job, name='apply_job'),
    path('thank-you/', views.thank_you, name='thank_you'),
]