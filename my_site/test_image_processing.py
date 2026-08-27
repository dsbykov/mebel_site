from io import BytesIO
from unittest import mock

from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from pillow_heif import from_pillow

from .forms import ProjectImageAdminForm
from .image_processing import optimize_portfolio_image, validate_portfolio_image
from .models import ProjectImage


def make_image_upload(size=(1200, 800), image_format='JPEG', name='photo.jpg', exif=None):
    buffer = BytesIO()
    image = Image.new('RGB', size, color=(126, 91, 68))
    save_options = {'quality': 96} if image_format == 'JPEG' else {}
    if exif is not None:
        save_options['exif'] = exif
    image.save(buffer, format=image_format, **save_options)
    image.close()
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=f'image/{image_format.lower()}')


def make_heic_upload(size=(1200, 800), name='photo.heic'):
    buffer = BytesIO()
    image = Image.new('RGB', size, color=(126, 91, 68))
    heif_file = from_pillow(image)
    heif_file.save(buffer, quality=90)
    image.close()
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/heic')


class PortfolioImageValidationTest(SimpleTestCase):
    def test_admin_image_field_accepts_heic_extension(self):
        upload = make_heic_upload()

        cleaned_upload = ProjectImageAdminForm.base_fields['image'].clean(upload)

        self.assertEqual(cleaned_upload.name, 'photo.heic')

    @override_settings(PORTFOLIO_IMAGE_MAX_UPLOAD_SIZE=10)
    def test_rejects_file_larger_than_upload_limit(self):
        upload = SimpleUploadedFile('large.jpg', b'x' * 11, content_type='image/jpeg')

        with self.assertRaisesMessage(ValidationError, '20 МБ'):
            validate_portfolio_image(upload)

    def test_rejects_corrupted_file(self):
        upload = SimpleUploadedFile('broken.jpg', b'not an image', content_type='image/jpeg')

        with self.assertRaisesMessage(ValidationError, 'повреждён'):
            validate_portfolio_image(upload)

    def test_rejects_unsupported_image_format(self):
        upload = make_image_upload(image_format='GIF', name='animated.gif')

        with self.assertRaisesMessage(ValidationError, 'JPEG, PNG, WebP, HEIC или HEIF'):
            validate_portfolio_image(upload)

    @override_settings(PORTFOLIO_IMAGE_MAX_SOURCE_SIDE=1000)
    def test_rejects_excessive_source_dimensions(self):
        upload = make_image_upload(size=(1001, 10), image_format='PNG', name='wide.png')

        with self.assertRaisesMessage(ValidationError, '16 000 пикселей'):
            validate_portfolio_image(upload)


class PortfolioImageOptimizationTest(SimpleTestCase):
    @override_settings(PORTFOLIO_IMAGE_MAX_OUTPUT_SIDE=800)
    def test_converts_heic_to_webp(self):
        upload = make_heic_upload(size=(1600, 1200))

        result = optimize_portfolio_image(upload)

        self.assertEqual(result.name, 'photo.webp')
        with Image.open(result) as processed:
            self.assertEqual(processed.format, 'WEBP')
            self.assertEqual(processed.size, (800, 600))

    @override_settings(PORTFOLIO_IMAGE_MAX_OUTPUT_SIDE=800, PORTFOLIO_IMAGE_WEBP_QUALITY=82)
    def test_converts_resizes_and_compresses_to_webp(self):
        upload = make_image_upload(size=(3200, 1600))
        source_size = upload.size

        result = optimize_portfolio_image(upload)

        self.assertTrue(result.name.endswith('.webp'))
        self.assertLess(result.size, source_size)
        with Image.open(result) as processed:
            self.assertEqual(processed.format, 'WEBP')
            self.assertEqual(processed.size, (800, 400))

    @override_settings(PORTFOLIO_IMAGE_MAX_OUTPUT_SIDE=200)
    def test_applies_exif_orientation_before_saving(self):
        exif = Image.Exif()
        exif[274] = 6
        upload = make_image_upload(size=(40, 80), exif=exif)

        result = optimize_portfolio_image(upload)

        with Image.open(result) as processed:
            self.assertEqual(processed.size, (80, 40))

    def test_returns_user_friendly_error_if_encoder_fails(self):
        upload = make_image_upload()
        with mock.patch('PIL.Image.Image.save', side_effect=OSError('encoder failed')):
            with self.assertRaisesMessage(ValidationError, 'Не удалось обработать фотографию'):
                optimize_portfolio_image(upload)

    @override_settings(PORTFOLIO_IMAGE_MAX_OUTPUT_SIDE=640)
    def test_model_converts_file_before_storage_save(self):
        project_image = ProjectImage(project_id=1, image=make_image_upload(size=(1280, 720)))

        with mock.patch('django.db.models.Model.save') as base_save:
            project_image.save()

        base_save.assert_called_once()
        self.assertTrue(project_image.image.name.endswith('.webp'))
        with Image.open(project_image.image.file) as processed:
            self.assertEqual(processed.format, 'WEBP')
            self.assertEqual(processed.size, (640, 360))
