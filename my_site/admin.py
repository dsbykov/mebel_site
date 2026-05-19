from django.contrib import admin
from .models import UserProfile, Review, Project, ProjectImage, Partner, SiteSettings


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


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website_url', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)


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
