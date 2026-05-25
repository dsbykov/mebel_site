from operator import concat

from django.shortcuts import render
from .models import Project, SiteSettings


def home(request):
    projects = Project.objects.prefetch_related('images').all()
    site_settings = SiteSettings.objects.first()
    return render(
        request, 'home.html', 
        {
            'projects': projects,
            'site_settings': site_settings,
        }
    )
