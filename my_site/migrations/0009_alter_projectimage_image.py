import my_site.image_processing
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('my_site', '0008_russian_admin_field_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectimage',
            name='image',
            field=models.ImageField(
                help_text='JPEG, PNG, WebP, HEIC или HEIF до 20 МБ; максимум 16 000 px по стороне и 80 Мп. Перед сохранением фотография автоматически уменьшается до 2560 px и преобразуется в WebP.',
                upload_to='portfolio/',
                validators=[my_site.image_processing.validate_portfolio_image],
                verbose_name='Файл изображения',
            ),
        ),
    ]
