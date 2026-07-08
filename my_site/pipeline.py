from .models import UserProfile


def create_user_profile(backend, user, response, *args, **kwargs):
    """
    Создает профиль пользователя при регистрации через социальную сеть.
    Выполняется после создания пользователя в pipeline social-auth.
    """
    if backend.name == 'yandex-oauth2':
        # Проверяем, существует ли уже профиль
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'yandex_id': response.get('id'),
                'username': response.get('login'),
                'email': response.get('default_email'),
                'first_name': response.get('first_name'),
                'last_name': response.get('last_name'),
                'avatar_url': response.get('avatar_url'),
            }
        )
        
        # Если профиль уже существовал (не был создан сейчас), обновляем данные
        if not created:
            profile.yandex_id = response.get('id')
            profile.username = response.get('login')
            profile.email = response.get('default_email')
            profile.first_name = response.get('first_name')
            profile.last_name = response.get('last_name')
            profile.avatar_url = response.get('avatar_url')
            profile.save()
    
    return {'user': user}