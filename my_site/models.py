from django.db import models

class UserProfile(models.Model):
    yandex_id = models.CharField(max_length=255, unique=True)  # ID из Яндекса
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or self.email or f"Yandex user {self.yandex_id}"


class Review(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.PositiveSmallIntegerField(verbose_name="Оценка", choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)  # можно модерировать

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

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/portfolio/')
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Описание изображения")

    def __str__(self):
        return f"Фото для {self.project.title}"


class Partner(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя партнёра")
    website_url = models.URLField(verbose_name="Сайт партнёра")
    logo = models.ImageField(upload_to='media/partners/', blank=True, null=True, verbose_name="Логотип")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SiteSettings(models.Model):
    business_description = models.TextField(verbose_name="Описание деятельности")
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True)
    yandex_map_link = models.URLField(blank=True, verbose_name="Ссылка на Яндекс.Карты")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Настройки сайта"