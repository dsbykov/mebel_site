from django.contrib import admin
from django import forms
from django.contrib import messages
from django.db.models import Count
from django.utils.html import format_html

from .models import UserProfile, Review, Project, ProjectImage, Partner, PartnerCategory, SiteSettings
from .forms import ProjectImageAdminForm
from .partner_preview import fetch_preview_image


admin.site.site_header = 'Панель управления'
admin.site.site_title = 'Администрирование сайта'
admin.site.index_title = 'Управление содержимым сайта'
admin.site.site_url = '/'
admin.site.empty_value_display = '—'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('yandex_id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
    search_fields = ('yandex_id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('date_joined',)
    readonly_fields = ('yandex_id', 'date_joined')
    list_per_page = 25
    ordering = ('-date_joined',)
    fieldsets = (
        ('Учётная запись', {'fields': ('user', 'yandex_id', 'username')}),
        ('Контактные данные', {'fields': ('first_name', 'last_name', 'email', 'avatar_url')}),
        ('Служебная информация', {'fields': ('date_joined',), 'classes': ('collapse',)}),
    )


@admin.action(description='Опубликовать выбранные отзывы')
def publish_reviews(modeladmin, request, queryset):
    updated = queryset.update(is_published=True)
    modeladmin.message_user(request, f'Опубликовано отзывов: {updated}.', messages.SUCCESS)


@admin.action(description='Снять выбранные отзывы с публикации')
def unpublish_reviews(modeladmin, request, queryset):
    updated = queryset.update(is_published=False)
    modeladmin.message_user(request, f'Скрыто отзывов: {updated}.', messages.SUCCESS)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'publication_status', 'created_at')
    list_filter = ('is_published', 'rating', 'created_at')
    search_fields = ('author__username', 'author__email', 'text')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('author',)
    date_hierarchy = 'created_at'
    actions = (publish_reviews, unpublish_reviews)
    list_per_page = 20
    ordering = ('-created_at',)
    fieldsets = (
        ('Отзыв', {'fields': ('author', 'text', 'rating')}),
        ('Публикация', {
            'fields': ('is_published', 'created_at', 'updated_at'),
            'description': 'Новые отзывы скрыты до проверки. Включите публикацию, когда текст готов к показу на сайте.',
        }),
    )

    @admin.display(description='Статус', ordering='is_published')
    def publication_status(self, obj):
        if obj.is_published:
            return format_html('<span class="admin-status admin-status--success">{}</span>', 'Опубликован')
        return format_html('<span class="admin-status admin-status--warning">{}</span>', 'Ожидает проверки')


class ProjectImageInline(admin.StackedInline):
    model = ProjectImage
    form = ProjectImageAdminForm
    extra = 1
    fields = ('image_preview', 'image', 'alt_text')
    readonly_fields = ('image_preview',)
    can_delete = True
    show_change_link = True
    verbose_name = 'Фотография проекта'
    verbose_name_plural = 'Фотографии проекта'

    @admin.display(description='Текущее изображение')
    def image_preview(self, obj):
        if obj and obj.pk and obj.image:
            return format_html(
                '<img class="admin-project-image-preview" src="{}" alt="Текущее фото проекта">',
                obj.image.url,
            )
        return 'Изображение появится здесь после загрузки и сохранения проекта.'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_thumbnail', 'title', 'photos_count', 'created_at')
    list_display_links = ('project_thumbnail', 'title')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    inlines = (ProjectImageInline,)
    date_hierarchy = 'created_at'
    list_per_page = 20
    ordering = ('-created_at',)
    fieldsets = (
        ('Содержание проекта', {'fields': ('title', 'description')}),
        ('Дополнительно', {
            'fields': ('featured_review', 'created_at'),
            'description': 'Рекомендуемый отзыв необязателен. Фотографии проекта добавляются ниже на этой же странице.',
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('images')

    @admin.display(description='Фото')
    def project_thumbnail(self, obj):
        image = next(iter(obj.images.all()), None)
        if image:
            return format_html('<img class="admin-list-thumbnail" src="{}" alt="">', image.image.url)
        return format_html('<span class="admin-list-placeholder">{}</span>', 'Нет фото')

    @admin.display(description='Фотографий')
    def photos_count(self, obj):
        return len(obj.images.all())


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    form = ProjectImageAdminForm
    list_display = ('image_thumbnail', 'project', 'alt_text')
    list_display_links = ('image_thumbnail', 'project')
    search_fields = ('project__title', 'alt_text')
    list_filter = ('project',)
    list_select_related = ('project',)
    list_per_page = 25
    fieldsets = (
        ('Фотография проекта', {
            'fields': ('project', 'image', 'alt_text'),
            'description': 'Выберите проект, загрузите изображение и добавьте понятное текстовое описание.',
        }),
    )

    @admin.display(description='Фото')
    def image_thumbnail(self, obj):
        return format_html('<img class="admin-list-thumbnail" src="{}" alt="">', obj.image.url)


@admin.register(PartnerCategory)
class PartnerCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'partners_count', 'sort_order')
    list_editable = ('sort_order',)
    search_fields = ('name',)
    fieldsets = (
        ('Раздел партнёров', {
            'fields': ('name', 'sort_order'),
            'description': 'Раздел объединяет партнёров одного типа и отображается отдельной строкой на главной странице.',
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_partners_count=Count('partners'))

    @admin.display(description='Партнёров', ordering='_partners_count')
    def partners_count(self, obj):
        return obj._partners_count


class PartnerAdminForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = '__all__'

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category is None:
            raise forms.ValidationError('Выберите раздел партнёра.')
        return category


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    form = PartnerAdminForm
    list_display = ('partner_thumbnail', 'name', 'category', 'website_link', 'sort_order', 'is_active')
    list_display_links = ('partner_thumbnail', 'name')
    list_editable = ('sort_order', 'is_active')
    search_fields = ('name', 'description', 'website_url')
    list_filter = ('category', 'is_active')
    readonly_fields = ('preview_card_image',)
    fieldsets = (
        (None, {'fields': ('name', 'category', 'website_url', 'description')}),
        ('Карточка', {
            'fields': ('logo', 'preview_card_image'),
            'description': 'Если логотип не загружен, изображение карточки будет автоматически получено со страницы партнёра.',
        }),
        ('Отображение', {'fields': ('sort_order', 'is_active')}),
    )
    list_select_related = ('category',)
    list_per_page = 20

    @admin.display(description='Карточка')
    def partner_thumbnail(self, obj):
        if obj.logo:
            return format_html('<img class="admin-list-thumbnail admin-list-thumbnail--contain" src="{}" alt="">', obj.logo.url)
        if obj.preview_image_url:
            return format_html('<img class="admin-list-thumbnail" src="{}" alt="">', obj.preview_image_url)
        return format_html('<span class="admin-list-placeholder">{}</span>', 'Нет фото')

    @admin.display(description='Сайт партнёра', ordering='website_url')
    def website_link(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Открыть ↗</a>', obj.website_url)

    @admin.display(description='Текущее изображение карточки')
    def preview_card_image(self, obj):
        if obj.logo:
            return format_html('<img src="{}" alt="" style="max-width:280px;max-height:160px;border-radius:12px">', obj.logo.url)
        if obj.preview_image_url:
            return format_html('<img src="{}" alt="" style="max-width:280px;max-height:160px;border-radius:12px">', obj.preview_image_url)
        return 'Изображение появится после сохранения ссылки или загрузки логотипа.'

    def save_model(self, request, obj, form, change):
        should_refresh = not obj.logo and (not obj.preview_image_url or 'website_url' in form.changed_data)
        if should_refresh:
            try:
                obj.preview_image_url = fetch_preview_image(obj.website_url) or ''
                if not obj.preview_image_url:
                    messages.warning(request, 'Сайт партнёра не предоставил изображение для карточки. Будет показана фирменная заглушка.')
            except (OSError, ValueError) as error:
                obj.preview_image_url = ''
                messages.warning(request, f'Не удалось получить изображение со страницы: {error}')
        super().save_model(request, obj, form, change)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('settings_summary', 'phone', 'email', 'updated_at')
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('О компании', {'fields': ('business_description',)}),
        ('Контактные данные', {
            'fields': ('phone', 'email', 'address', 'yandex_map_link'),
            'description': 'Эти данные отображаются в контактном блоке и используются посетителями для связи.',
        }),
        ('Служебная информация', {'fields': ('updated_at',), 'classes': ('collapse',)}),
    )

    @admin.display(description='Настройки')
    def settings_summary(self, obj):
        return 'Основная информация о компании и контакты'

    def has_add_permission(self, request):
        # Запрещаем добавлять более одной записи
        return SiteSettings.objects.count() == 0

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление
        return False
