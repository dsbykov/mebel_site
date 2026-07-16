"""
Скрипт для проверки неиспользуемых медиафайлов
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.conf import settings
from my_site.models import ProjectImage, Partner


def get_used_images():
    """Получить список используемых изображений из БД"""
    used = set()
    for img in ProjectImage.objects.all():
        if img.image:
            used.add(str(img.image))
    for partner in Partner.objects.all():
        if partner.logo:
            used.add(str(partner.logo))
    return used


if __name__ == '__main__':
    print("Проверка неиспользуемых медиафайлов...")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print()
    
    used = get_used_images()
    print('Используемые файлы в БД:')
    for f in used:
        print(f'  {f}')
    
    media_subdir = 'portfolio'
    full_path = os.path.join(settings.MEDIA_ROOT, media_subdir)
    print(f'\nФайлы на диске ({full_path}):')
    
    if os.path.exists(full_path):
        for filename in os.listdir(full_path):
            filepath = os.path.join(full_path, filename)
            if os.path.isfile(filepath):
                relative_path = os.path.join(media_subdir, filename).replace('\\', '/')
                is_used = relative_path in used
                status = 'ИСПОЛЬЗУЕТСЯ' if is_used else 'НЕИСПОЛЬЗУЕТСЯ'
                print(f'  {filename} - {status}')
    else:
        print(f'  Директория не существует: {full_path}')
