import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('my_site', '0007_partner_categories_and_cards'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(model_name='partner', name='description', field=models.TextField(blank=True, help_text='Короткое описание продукции или услуг партнёра; рекомендуется 1–2 предложения.', verbose_name='Описание')),
        migrations.AlterField(model_name='partner', name='logo', field=models.ImageField(blank=True, help_text='Необязательно. Если файл не выбран, сайт попробует получить изображение по ссылке партнёра.', null=True, upload_to='partners/', verbose_name='Логотип')),
        migrations.AlterField(model_name='partner', name='name', field=models.CharField(help_text='Отображается поверх карточки партнёра.', max_length=100, verbose_name='Название партнёра')),
        migrations.AlterField(model_name='partner', name='sort_order', field=models.PositiveIntegerField(default=0, help_text='Чем меньше число, тем раньше карточка показана внутри раздела.', verbose_name='Порядок отображения')),
        migrations.AlterField(model_name='partner', name='website_url', field=models.URLField(help_text='Полная ссылка, которая откроется при нажатии на карточку.', verbose_name='Сайт партнёра')),
        migrations.AlterField(model_name='partnercategory', name='name', field=models.CharField(help_text='Например: «Фурнитура», «Фасады» или «Столешницы».', max_length=100, unique=True, verbose_name='Название раздела')),
        migrations.AlterField(model_name='partnercategory', name='sort_order', field=models.PositiveIntegerField(default=0, help_text='Чем меньше число, тем выше раздел расположен на странице.', verbose_name='Порядок отображения')),
        migrations.AlterField(model_name='project', name='created_at', field=models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
        migrations.AlterField(model_name='project', name='description', field=models.TextField(blank=True, help_text='Кратко расскажите о задаче, материалах и результате работы.', verbose_name='Описание')),
        migrations.AlterField(model_name='project', name='featured_review', field=models.OneToOneField(blank=True, help_text='Необязательный отзыв, связанный с этим проектом.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='featured_in_project', to='my_site.review', verbose_name='Рекомендуемый отзыв')),
        migrations.AlterField(model_name='project', name='title', field=models.CharField(help_text='Отображается в карточке и окне просмотра проекта.', max_length=200, verbose_name='Название проекта')),
        migrations.AlterField(model_name='projectimage', name='alt_text', field=models.CharField(blank=True, help_text='Краткое описание фотографии для доступности и поисковых систем.', max_length=200, verbose_name='Описание изображения')),
        migrations.AlterField(model_name='projectimage', name='image', field=models.ImageField(help_text='Фотография будет показана в карточке и галерее проекта.', upload_to='portfolio/', verbose_name='Файл изображения')),
        migrations.AlterField(model_name='review', name='author', field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='my_site.userprofile', verbose_name='Автор')),
        migrations.AlterField(model_name='review', name='created_at', field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
        migrations.AlterField(model_name='review', name='is_published', field=models.BooleanField(default=False, help_text='Включите, чтобы отзыв появился на главной странице.', verbose_name='Опубликован')),
        migrations.AlterField(model_name='review', name='text', field=models.TextField(help_text='Текст отображается в разделе «Отзывы наших клиентов» после публикации.', verbose_name='Текст отзыва')),
        migrations.AlterField(model_name='review', name='updated_at', field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
        migrations.AlterField(model_name='sitesettings', name='address', field=models.CharField(blank=True, help_text='Фактический адрес, отображаемый в контактах.', max_length=255, verbose_name='Адрес компании')),
        migrations.AlterField(model_name='sitesettings', name='business_description', field=models.TextField(help_text='Основной текст о компании на главной странице.', verbose_name='Описание деятельности')),
        migrations.AlterField(model_name='sitesettings', name='email', field=models.EmailField(help_text='Контактный адрес электронной почты на сайте.', max_length=254, verbose_name='Электронная почта')),
        migrations.AlterField(model_name='sitesettings', name='phone', field=models.CharField(blank=True, help_text='Контактный номер в блоке «Контакты».', max_length=20, verbose_name='Номер телефона')),
        migrations.AlterField(model_name='sitesettings', name='yandex_map_link', field=models.URLField(blank=True, help_text='Полная ссылка на организацию или точку на Яндекс.Картах.', verbose_name='Ссылка на Яндекс.Карты')),
        migrations.AlterField(model_name='userprofile', name='avatar_url', field=models.URLField(blank=True, null=True, verbose_name='Ссылка на аватар')),
        migrations.AlterField(model_name='userprofile', name='date_joined', field=models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
        migrations.AlterField(model_name='userprofile', name='email', field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Электронная почта')),
        migrations.AlterField(model_name='userprofile', name='first_name', field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Имя')),
        migrations.AlterField(model_name='userprofile', name='last_name', field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Фамилия')),
        migrations.AlterField(model_name='userprofile', name='user', field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
        migrations.AlterField(model_name='userprofile', name='username', field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Имя пользователя')),
        migrations.AlterField(model_name='userprofile', name='yandex_id', field=models.CharField(max_length=255, unique=True, verbose_name='ID Яндекса')),
    ]
