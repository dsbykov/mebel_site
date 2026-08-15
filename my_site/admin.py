from django.contrib import admin
from django import forms
from django.contrib import messages

from .models import UserProfile, Review, Project, ProjectImage, Partner, PartnerCategory, SiteSettings
from .partner_preview import fetch_preview_image


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('yandex_id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
    search_fields = ('yandex_id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('date_joined',)
    readonly_fields = ('yandex_id', 'date_joined')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'rating', 'created_at')
    search_fields = ('author__username', 'text')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'featured_review')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'alt_text')
    search_fields = ('project__title', 'alt_text')
    list_filter = ('project',)


@admin.register(PartnerCategory)
class PartnerCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')
    list_editable = ('sort_order',)
    search_fields = ('name',)


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
    list_display = ('name', 'category', 'website_url', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    search_fields = ('name', 'description', 'website_url')
    list_filter = ('category', 'is_active')
    readonly_fields = ('preview_image_url',)
    fieldsets = (
        (None, {'fields': ('name', 'category', 'website_url', 'description')}),
        ('Карточка', {
            'fields': ('logo', 'preview_image_url'),
            'description': 'Если логотип не загружен, изображение карточки будет автоматически получено со страницы партнёра.',
        }),
        ('Отображение', {'fields': ('sort_order', 'is_active')}),
    )

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
    list_display = ('business_description', 'phone', 'email', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Запрещаем добавлять более одной записи
        return SiteSettings.objects.count() == 0

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление
        return False
