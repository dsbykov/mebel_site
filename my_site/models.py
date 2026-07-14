from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os
import shutil
import logging

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='userprofile', null=True, blank=True)
    yandex_id = models.CharField(max_length=255, unique=True)  # ID из Яндекса
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return self.username or self.email or f"Yandex user {self.yandex_id}"


class Review(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.PositiveSmallIntegerField(
        verbose_name="Оценка",
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)  # можно модерировать, по умолчанию не опубликован, требует модерации

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв от {self.author} — {self.rating}★"
    

class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название проекта")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    featured_review = models.OneToOneField(
        Review,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_in_project',
        verbose_name="Рекомендуемый отзыв"
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE, verbose_name="Проект")
    image = models.ImageField(upload_to='portfolio/', verbose_name="Файл изображения")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Описание изображения")

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фотографии"

    def __str__(self):
        return f"Фото для {self.project.title}"

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения с диска перед удалением записи из БД
        if self.image:
            image_str = str(self.image)
            logger.debug(f"Удаляем файл '{image_str}' с диска.")
            # Django сохраняет путь относительно MEDIA_ROOT
            # Если в БД путь начинается с 'media/', убираем его, так как MEDIA_ROOT уже содержит 'media'
            if image_str.startswith('media/'):
                image_path = os.path.join(settings.MEDIA_ROOT, image_str.replace('media/', '', 1))
            else:
                image_path = os.path.join(settings.MEDIA_ROOT, image_str)
            
            if os.path.isfile(image_path):
                os.remove(image_path)
                logger.info(f'Файл "{image_path}" удален.')
            else:
                logger.warning(f'Файл не найден: {image_path}')
        super().delete(*args, **kwargs)


class Partner(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя партнёра")
    website_url = models.URLField(verbose_name="Сайт партнёра")
    logo = models.ImageField(upload_to='partners/', blank=True, null=True, verbose_name="Логотип")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Партнёр"
        verbose_name_plural = "Партнёры"

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Удаляем файл логотипа с диска перед удалением записи из БД
        if self.logo:
            logo_str = str(self.logo)
            logger.debug(f"Удаляем файл '{logo_str}' с диска.")
            # Если в БД путь начинается с 'media/', убираем его, так как MEDIA_ROOT уже содержит 'media'
            if logo_str.startswith('media/'):
                logo_path = os.path.join(settings.MEDIA_ROOT, logo_str.replace('media/', '', 1))
            else:
                logo_path = os.path.join(settings.MEDIA_ROOT, logo_path)
            
            if os.path.isfile(logo_path):
                os.remove(logo_path)
                logger.info(f'Файл "{logo_path}" удален.')
            else:
                logger.warning(f'Файл не найден: {logo_path}')
        super().delete(*args, **kwargs)


class SiteSettings(models.Model):
    business_description = models.TextField(verbose_name="Описание деятельности")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Номер мобильного")
    email = models.EmailField(verbose_name="Электронная почта")
    address = models.CharField(max_length=255, blank=True, verbose_name="Адресс компании")
    yandex_map_link = models.URLField(blank=True, verbose_name="Ссылка на Яндекс.Карты")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"
    
    def __str__(self):
        return "Настройки сайта"
    
    def save(self, *args, **kwargs):
        # Singleton: всегда обновляем первую запись, если она существует
        if SiteSettings.objects.exists():
            existing = SiteSettings.objects.first()
            # Обновляем поля существующей записи
            existing.business_description = self.business_description
            existing.phone = self.phone
            existing.email = self.email
            existing.address = self.address
            existing.yandex_map_link = self.yandex_map_link
            # Используем save_base() с update_fields для избежания рекурсии
            existing.save_base(update_fields=['business_description', 'phone', 'email', 'address', 'yandex_map_link'])
            # Возвращаем сохраненный объект
            return existing
        return super().save(*args, **kwargs)


# Сигнал для удаления всех изображений проекта при удалении проекта
@receiver(pre_delete, sender=Project)
def delete_project_images(sender, instance, **kwargs):
    """Удаляет все изображения проекта при удалении проекта"""
    logger.debug(f"DELETE IMAGES: Удаляем все фото относящиеся к проекту '{instance.title}'")
    for image in instance.images.all():
        logger.debug(f"DELETE IMAGES: Удаляем фото: '{image.image}'")
        if image.image:
            image_str = str(image.image)
            # Если в БД путь начинается с 'media/', убираем его, так как MEDIA_ROOT уже содержит 'media'
            if image_str.startswith('media/'):
                image_path = os.path.join(settings.MEDIA_ROOT, image_str.replace('media/', '', 1))
            else:
                image_path = os.path.join(settings.MEDIA_ROOT, image_str)
            
            if os.path.isfile(image_path):
                try:
                    os.remove(image_path)
                    logger.info(f"DELETE IMAGES: Файл '{image_path}' удален.")
                except Exception as e:
                    # Логируем ошибку, но не прерываем удаление
                    logger.error(f"DELETE IMAGES: Ошибка при попытке удаления файла {image.image}: {e}")
            else:
                logger.warning(f"DELETE IMAGES: Файл не найден: {image_path}")
