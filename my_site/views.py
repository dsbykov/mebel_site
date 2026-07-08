from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Project, SiteSettings, Review, UserProfile
from .forms import ReviewForm
from .utils import login_required
import logging 

logger = logging.getLogger(__name__)


def load_reviews(request):
    """AJAX endpoint для загрузки отзывов с пагинацией"""
    # Убрали проверку на AJAX-запрос, чтобы работало с fetch API
    page_number = request.GET.get('page', 1)
    
    reviews_list = Review.objects.filter(is_published=True).order_by('-created_at')
    
    paginator = Paginator(reviews_list, 3)  # 3 отзыва на страницу
    
    try:
        reviews = paginator.page(page_number)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        return JsonResponse({'error': 'No more reviews'}, status=404)
    
    # Рендерим только блок отзывов
    from django.template.loader import render_to_string
    html = render_to_string('partials/reviews_list.html', {
        'reviews': reviews,
    })
    
    return JsonResponse({
        'html': html,
        'current_page': reviews.number,
        'num_pages': paginator.num_pages,
        'has_next': reviews.has_next(),
        'has_previous': reviews.has_previous(),
    })


def home(request):
    projects = Project.objects.prefetch_related('images').all()
    site_settings = SiteSettings.objects.first()
    reviews_list = Review.objects.filter(is_published=True).order_by('-created_at')
    
    # Пагинация: по 3 отзыва на страницу
    paginator = Paginator(reviews_list, 3)
    page = request.GET.get('reviews_page', 1)
    
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    
    logger.debug(f"reviews = {list(reviews)}")
    logger.info(f"Number of reviews: {reviews_list.count()}")
    return render(
        request, 'home.html', 
        {
            'projects': projects,
            'site_settings': site_settings,
            'reviews': reviews,
            'reviews_paginator': paginator,
            'reviews_json': {
                'current_page': reviews.number,
                'num_pages': paginator.num_pages,
                'has_next': reviews.has_next(),
                'has_previous': reviews.has_previous(),
            },
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
