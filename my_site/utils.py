import logging
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from social_django.models import UserSocialAuth

logger = logging.getLogger(__name__)

def is_token_expired(extra_data):
    """
    Проверяет, истек ли срок действия токена.
    Возвращает True, если токен истек или отсутствует информация о сроке действия.
    Учитывает, что Яндекс OAuth2 может не возвращать срок действия токена.
    """
    if not extra_data:
        logger.warning("No extra_data available")
        return True
    
    # Проверяем наличие обязательных полей
    if 'access_token' not in extra_data:
        logger.warning("No access_token in extra_data")
        return True
    
    # Если есть expires, используем его для проверки
    if 'expires' in extra_data:
        expires_at = extra_data['expires']
        current_timestamp = timezone.now().timestamp()
        logger.debug(f"Token expiration check: current_time={current_timestamp}, expires_at={expires_at}, time_left={(expires_at - current_timestamp) if expires_at > current_timestamp else 0} seconds")
        return current_timestamp >= expires_at
    
    # Если нет expires, используем auth_time и предполагаем стандартный срок действия (3600 секунд для Яндекс OAuth2)
    if 'auth_time' in extra_data:
        auth_time = extra_data['auth_time']
        token_lifetime = 3600  # Стандартный срок жизни токена Яндекс OAuth2
        expires_at = auth_time + token_lifetime
        current_timestamp = timezone.now().timestamp()
        time_left = expires_at - current_timestamp
        
        logger.debug(f"No expires in extra_data, using auth_time: auth_time={auth_time}, current_time={current_timestamp}, expires_at={expires_at}, time_left={time_left} seconds")
        
        return current_timestamp >= expires_at
    
    # Если нет ни expires, ни auth_time, считаем токен просроченным
    logger.warning("No expires and no auth_time in extra_data")
    return True

def ensure_valid_token(user):
    """
    Проверяет валидность токена OAuth пользователя.
    Возвращает True, если токен действителен, False в противном случае.
    """
    try:
        social_auth = UserSocialAuth.objects.get(user=user, provider='yandex-oauth2')
        logger.debug(f"Checking token for user {user.username}: {social_auth.extra_data}")
        if is_token_expired(social_auth.extra_data):
            logger.warning(f"OAuth token expired for user {user.username}")
            return False
        return True
    except UserSocialAuth.DoesNotExist:
        logger.warning(f"No social auth found for user {user.username}")
        return False

def login_required(view_func=None, redirect_field_name='next', login_url=None):
    """
    Кастомный декоратор login_required, который проверяет:
    1. Аутентификацию пользователя
    2. Наличие профиля UserProfile
    3. Валидность токена OAuth
    
    При необходимости выводит сообщение о необходимости повторной авторизации.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Проверка аутентификации
            if not request.user.is_authenticated:
                if login_url:
                    return redirect(login_url)
                return redirect(reverse('social:begin', args=['yandex-oauth2']))
            
            # Проверка наличия профиля пользователя
            try:
                if not hasattr(request.user, 'userprofile') or request.user.userprofile is None:
                    logger.warning(f"UserProfile not found for user {request.user.username}")
                    messages.error(request, 'Профиль пользователя не найден. Пожалуйста, войдите снова.')
                    return redirect(reverse('social:begin', args=['yandex-oauth2']))
            except Exception as e:
                logger.error(f"Error checking user profile: {e}")
                messages.error(request, 'Произошла ошибка при проверке профиля. Пожалуйста, войдите снова.')
                return redirect(reverse('social:begin', args=['yandex-oauth2']))
            
            # Проверка валидности токена
            if not ensure_valid_token(request.user):
                messages.warning(request, 'Срок действия вашей сессии истек. Пожалуйста, войдите снова для продолжения.')
                return redirect(reverse('social:begin', args=['yandex-oauth2']))
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if view_func:
        return decorator(view_func)
    return decorator