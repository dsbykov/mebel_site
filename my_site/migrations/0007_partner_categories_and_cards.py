from django.db import migrations, models
import django.db.models.deletion


def create_default_partner_categories(apps, schema_editor):
    PartnerCategory = apps.get_model('my_site', 'PartnerCategory')
    for sort_order, name in enumerate(
        ('Фурнитура', 'Фасады', 'Столешницы', 'Системы хранения', 'Материалы'),
        start=1,
    ):
        PartnerCategory.objects.get_or_create(
            name=name,
            defaults={'sort_order': sort_order * 10},
        )


class Migration(migrations.Migration):
    dependencies = [('my_site', '0006_load_default_settings')]

    operations = [
        migrations.CreateModel(
            name='PartnerCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название раздела')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Порядок отображения')),
            ],
            options={'verbose_name': 'Раздел партнёров', 'verbose_name_plural': 'Разделы партнёров', 'ordering': ('sort_order', 'name')},
        ),
        migrations.RunPython(create_default_partner_categories, migrations.RunPython.noop),
        migrations.AddField(model_name='partner', name='category', field=models.ForeignKey(help_text='Выберите существующий раздел или создайте новый кнопкой «+».', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='partners', to='my_site.partnercategory', verbose_name='Раздел')),
        migrations.AddField(model_name='partner', name='description', field=models.TextField(blank=True, verbose_name='Описание')),
        migrations.AddField(model_name='partner', name='preview_image_url', field=models.URLField(blank=True, editable=False, max_length=1000, verbose_name='Изображение со страницы')),
        migrations.AddField(model_name='partner', name='sort_order', field=models.PositiveIntegerField(default=0, verbose_name='Порядок отображения')),
        migrations.AlterField(model_name='partner', name='is_active', field=models.BooleanField(default=True, verbose_name='Показывать на сайте')),
        migrations.AlterModelOptions(name='partner', options={'ordering': ('category__sort_order', 'category__name', 'sort_order', 'name'), 'verbose_name': 'Партнёр', 'verbose_name_plural': 'Партнёры'}),
    ]
