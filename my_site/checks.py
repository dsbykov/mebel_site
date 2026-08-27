from PIL import features
from django.core.checks import Error, register

from .image_processing import HEIF_SUPPORT_AVAILABLE


@register()
def check_webp_encoder(app_configs, **kwargs):
    if features.check('webp'):
        return []
    return [
        Error(
            'Pillow собран без поддержки WebP.',
            hint='Установите сборку Pillow с libwebp: без неё фотографии портфолио нельзя сохранить.',
            id='my_site.E001',
        )
    ]


@register()
def check_heif_decoder(app_configs, **kwargs):
    if HEIF_SUPPORT_AVAILABLE:
        return []
    return [
        Error(
            'Декодер HEIC/HEIF недоступен.',
            hint='Установите pillow-heif: без него фотографии HEIC/HEIF нельзя обработать.',
            id='my_site.E002',
        )
    ]
