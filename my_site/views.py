from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Project, SiteSettings, Review, UserProfile
from .forms import ReviewForm
from .utils import login_required
import logging 

logger = logging.getLogger(__name__)



def home(request):
    projects = Project.objects.prefetch_related('images').all()
    site_settings = SiteSettings.objects.first()
    reviews = Review.objects.filter(is_published=True)
    logger.debug(f"reviews = {list(reviews)}")
    logger.info(f"Number of reviews: {reviews.count()}")
    return render(
        request, 'home.html', 
        {
            'projects': projects,
            'site_settings': site_settings,
            'reviews': reviews,
        }
    )


@login_required
@require_http_methods(["POST"])
def create_review(request):
    logger.info("Добавление нового отзыва")
    logger.debug(f"request.POST = {request.POST}")
    form = ReviewForm(request.POST)
    if form.is_valid():
        logger.debug(f"form.cleaned_data = {form.cleaned_data}")
        review = form.save(commit=False)
        review.author = request.user.userprofile
        review.save()
        logger.info(f"Review created: {review}")
        
        # Добавляем сообщение об успехе
        messages.success(request, 'Спасибо за ваш отзыв! Он будет опубликован после модерации.')
        
        # Возвращаем JSON-ответ вместо редиректа
        return JsonResponse({
            'success': True,
            'message': 'Спасибо за ваш отзыв! Он будет опубликован после модерации.'
        })
    
    # Если форма невалидна, возвращаем ошибки
    logger.warning(f"Form errors: {form.errors}")
    return JsonResponse({
        'success': False,
        'errors': form.errors
    })