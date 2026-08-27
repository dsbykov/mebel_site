"""Проверка, преобразование и сжатие фотографий портфолио."""

import logging
import warnings
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.text import slugify

try:
    from pillow_heif import register_heif_opener
except ImportError:
    HEIF_SUPPORT_AVAILABLE = False
else:
    register_heif_opener()
    HEIF_SUPPORT_AVAILABLE = True


logger = logging.getLogger(__name__)

ALLOWED_IMAGE_FORMATS = {'JPEG', 'PNG', 'WEBP', 'HEIF'}
ALLOWED_IMAGE_FORMAT_NAMES = 'JPEG, PNG, WebP, HEIC или HEIF'


def _setting(name, default):
    return getattr(settings, name, default)


def _reset_file(file):
    try:
        file.seek(0)
    except (AttributeError, OSError):
        pass


def validate_portfolio_image(file):
    """Проверяет размер, формат, целостность и безопасные размеры изображения."""
    if not file:
        return

    max_size = _setting('PORTFOLIO_IMAGE_MAX_UPLOAD_SIZE', 20 * 1024 * 1024)
    file_size = getattr(file, 'size', None)
    if file_size is not None and file_size > max_size:
        raise ValidationError(
            'Размер фотографии не должен превышать 20 МБ.',
            code='portfolio_image_too_large',
        )

    try:
        _reset_file(file)
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(file) as image:
                image_format = (image.format or '').upper()
                width, height = image.size
                frame_count = getattr(image, 'n_frames', 1)
                image.verify()

        if image_format not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError(
                f'Поддерживаются только форматы {ALLOWED_IMAGE_FORMAT_NAMES}.',
                code='portfolio_image_invalid_format',
            )
        if frame_count > 1:
            raise ValidationError(
                'Анимированные изображения для портфолио не поддерживаются.',
                code='portfolio_image_animated',
            )

        max_side = _setting('PORTFOLIO_IMAGE_MAX_SOURCE_SIDE', 16_000)
        max_pixels = _setting('PORTFOLIO_IMAGE_MAX_SOURCE_PIXELS', 80_000_000)
        if width <= 0 or height <= 0 or width > max_side or height > max_side:
            raise ValidationError(
                'Ширина и высота исходной фотографии не должны превышать 16 000 пикселей.',
                code='portfolio_image_dimensions_too_large',
            )
        if width * height > max_pixels:
            raise ValidationError(
                'Разрешение исходной фотографии не должно превышать 80 мегапикселей.',
                code='portfolio_image_pixels_too_large',
            )
    except ValidationError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ValidationError(
            'Разрешение фотографии слишком велико для безопасной обработки.',
            code='portfolio_image_unsafe_dimensions',
        )
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError) as error:
        logger.warning('Не удалось проверить фотографию портфолио: %s', error)
        raise ValidationError(
            'Файл повреждён или не является поддерживаемым изображением.',
            code='portfolio_image_invalid',
        ) from error
    finally:
        _reset_file(file)

    try:
        file._portfolio_image_validated = True
    except AttributeError:
        pass


def optimize_portfolio_image(file):
    """Возвращает подготовленный ContentFile в WebP, не сохраняя исходник на диск."""
    if not getattr(file, '_portfolio_image_validated', False):
        validate_portfolio_image(file)

    output = BytesIO()
    processed_image = None
    try:
        _reset_file(file)
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(file) as source:
                source.load()
                icc_profile = source.info.get('icc_profile')
                processed_image = ImageOps.exif_transpose(source)

        has_transparency = (
            processed_image.mode in {'RGBA', 'LA'}
            or (processed_image.mode == 'P' and 'transparency' in processed_image.info)
        )
        converted_image = processed_image.convert('RGBA' if has_transparency else 'RGB')
        if converted_image is not processed_image:
            processed_image.close()
            processed_image = converted_image

        max_side = _setting('PORTFOLIO_IMAGE_MAX_OUTPUT_SIDE', 2_560)
        processed_image.thumbnail(
            (max_side, max_side),
            Image.Resampling.LANCZOS,
            reducing_gap=3.0,
        )

        save_options = {
            'format': 'WEBP',
            'quality': _setting('PORTFOLIO_IMAGE_WEBP_QUALITY', 82),
            'method': 6,
            'exact': False,
        }
        if has_transparency:
            save_options['alpha_quality'] = 90
        if icc_profile:
            save_options['icc_profile'] = icc_profile
        processed_image.save(output, **save_options)

        stem = slugify(Path(getattr(file, 'name', 'photo')).stem, allow_unicode=True) or 'photo'
        result = ContentFile(output.getvalue(), name=f'{stem}.webp')
        result._portfolio_image_validated = True
        result._portfolio_image_optimized = True
        logger.info(
            'Фотография портфолио преобразована в WebP: %s, %sx%s, %s байт',
            result.name,
            processed_image.width,
            processed_image.height,
            result.size,
        )
        return result
    except ValidationError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ValidationError(
            'Разрешение фотографии слишком велико для безопасной обработки.',
            code='portfolio_image_unsafe_dimensions',
        )
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError, MemoryError) as error:
        logger.exception('Ошибка преобразования фотографии портфолио')
        raise ValidationError(
            'Не удалось обработать фотографию. Проверьте файл и попробуйте загрузить его снова.',
            code='portfolio_image_processing_failed',
        ) from error
    finally:
        _reset_file(file)
        if processed_image is not None:
            processed_image.close()
        output.close()
