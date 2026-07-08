from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile, Review, Project, ProjectImage, Partner, SiteSettings


class UserProfileModelTest(TestCase):
    """Тесты для модели UserProfile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            username=self.user.username,
            yandex_id='123456',
            first_name='Иван',
            last_name='Иванов',
            avatar_url='https://example.com/avatar.jpg'
        )
    
    def test_user_profile_creation(self):
        """Проверка создания профиля пользователя"""
        self.assertEqual(self.user_profile.yandex_id, '123456')
        self.assertEqual(self.user_profile.first_name, 'Иван')
        self.assertEqual(self.user_profile.last_name, 'Иванов')
        self.assertEqual(str(self.user_profile), 'testuser')
    
    def test_user_profile_string_representation(self):
        """Проверка строкового представления профиля"""
        profile = UserProfile(yandex_id='7890')
        self.assertEqual(str(profile), 'Yandex user 7890')
        
        profile.username = 'user123'
        self.assertEqual(str(profile), 'user123')
        
        profile.username = ''
        profile.email = 'email@test.com'
        self.assertEqual(str(profile), 'email@test.com')


class ReviewModelTest(TestCase):
    """Тесты для модели Review"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewer',
            password='pass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            yandex_id='111111'
        )
        self.review = Review.objects.create(
            author=self.user_profile,
            text='Отличная работа!',
            rating=5
        )
    
    def test_review_creation(self):
        """Проверка создания отзыва"""
        self.assertEqual(self.review.text, 'Отличная работа!')
        self.assertEqual(self.review.rating, 5)
        self.assertFalse(self.review.is_published)
        self.assertIsNotNone(self.review.created_at)
        
    def test_review_string_representation(self):
        """Проверка строкового представления отзыва"""
        expected_str = f"Отзыв от {self.user_profile} — 5★"
        self.assertEqual(str(self.review), expected_str, msg="Фактический результат = " + str(self.review))
    
    def test_rating_choices(self):
        """Проверка допустимых значений рейтинга"""
        # Попробуем создать отзыв с недопустимым рейтингом
        review = Review(author=self.user_profile, text='Тест', rating=6)
        with self.assertRaises(Exception):
            review.full_clean()  # Вызываем валидацию
            review.save()
        
        # Проверим, что допустимые значения работают
        for i in range(1, 6):
            review = Review.objects.create(
                author=self.user_profile,
                text=f'Рейтинг {i}',
                rating=i
            )
            self.assertEqual(review.rating, i)


class ProjectModelTest(TestCase):
    """Тесты для модели Project"""
    
    def setUp(self):
        self.project = Project.objects.create(
            title='Тестовый проект',
            description='Описание тестового проекта'
        )
    
    def test_project_creation(self):
        """Проверка создания проекта"""
        self.assertEqual(self.project.title, 'Тестовый проект')
        self.assertEqual(self.project.description, 'Описание тестового проекта')
        self.assertIsNotNone(self.project.created_at)
        
    def test_project_string_representation(self):
        """Проверка строкового представления проекта"""
        self.assertEqual(str(self.project), 'Тестовый проект')
    
    def test_featured_review_relationship(self):
        """Проверка связи с рекомендуемым отзывом"""
        user = User.objects.create_user(username='author', password='pass')
        user_profile = UserProfile.objects.create(user=user, yandex_id='222222')
        review = Review.objects.create(author=user_profile, text='Хорошо', rating=4)
        
        self.project.featured_review = review
        self.project.save()
        
        self.assertEqual(self.project.featured_review, review)
        self.assertEqual(review.featured_in_project, self.project)


class ProjectImageModelTest(TestCase):
    """Тесты для модели ProjectImage"""
    
    def setUp(self):
        self.project = Project.objects.create(title='Проект с изображениями')
        
    def test_project_image_creation(self):
        """Проверка создания изображения проекта"""
        image = ProjectImage.objects.create(
            project=self.project,
            image='media/portfolio/test.jpg',
            alt_text='Тестовое изображение'
        )
        
        self.assertEqual(image.project, self.project)
        self.assertEqual(image.alt_text, 'Тестовое изображение')
        self.assertEqual(str(image), f'Фото для {self.project.title}')


class PartnerModelTest(TestCase):
    """Тесты для модели Partner"""
    
    def test_partner_creation(self):
        """Проверка создания партнера"""
        partner = Partner.objects.create(
            name='Тестовый партнёр',
            website_url='https://partner.com',
            is_active=True
        )
        
        self.assertEqual(partner.name, 'Тестовый партнёр')
        self.assertEqual(partner.website_url, 'https://partner.com')
        self.assertTrue(partner.is_active)
        self.assertEqual(str(partner), 'Тестовый партнёр')


class SiteSettingsModelTest(TestCase):
    """Тесты для модели SiteSettings"""
    
    def test_site_settings_creation(self):
        """Проверка создания настроек сайта"""
        settings = SiteSettings.objects.create(
            business_description='Описание деятельности компании',
            phone='+79991234567',
            email='info@company.com',
            address='г. Москва, ул. Тестовая, д. 1',
            # yandex_map_link='https://yandex.ru/maps/org/company/123456789'
        )
        
        self.assertEqual(settings.business_description, 'Описание деятельности компании')
        self.assertEqual(settings.phone, '+79991234567')
        self.assertEqual(settings.email, 'info@company.com')
        self.assertEqual(settings.address, 'г. Москва, ул. Тестовая, д. 1')
        # self.assertEqual(settings.yandex_map_link, 'https://yandex.ru/maps/org/company/123456789')
        self.assertIsNotNone(settings.updated_at)
        self.assertEqual(str(settings), 'Настройки сайта')
        
        # Проверка, изменеия записи
        SiteSettings.objects.create(
            business_description='Другие настройки',
            email='other@company.com'
        )
        self.assertEqual(SiteSettings.objects.count(), 1)
        # Обновляем объект из базы данных, чтобы увидеть изменения
        settings = SiteSettings.objects.first()
        self.assertEqual(settings.business_description, 'Другие настройки')
        self.assertEqual(settings.email, 'other@company.com')
        self.assertEqual(settings.phone, '')
        self.assertEqual(settings.address, '')


    def test_site_settings_updating(self):
        """Проверка обновления настроек сайта"""
        settings = SiteSettings.objects.create(
            business_description='Описание деятельности компании',
            phone='+79991234567',
            email='info@company.com',
            address='г. Москва, ул. Тестовая, д. 1',
        )
        # Проверяем
        self.assertEqual(settings.business_description, 'Описание деятельности компании')
        self.assertEqual(settings.phone, '+79991234567')
        self.assertEqual(settings.email, 'info@company.com')
        self.assertEqual(settings.address, 'г. Москва, ул. Тестовая, д. 1')
        # self.assertEqual(settings.yandex_map_link, 'https://yandex.ru/maps/org/company/123456789')
        self.assertIsNotNone(settings.updated_at)
        self.assertEqual(str(settings), 'Настройки сайта')

                # Проверка, изменеия записи
        SiteSettings.objects.update(
            business_description='Другие настройки',
            email='other@company.com'
        )
        self.assertEqual(SiteSettings.objects.count(), 1)
        # Обновляем объект из базы данных, чтобы увидеть изменения
        settings = SiteSettings.objects.first()
        self.assertEqual(settings.business_description, 'Другие настройки')
        self.assertEqual(settings.email, 'other@company.com')
        self.assertEqual(settings.phone, '+79991234567')
        self.assertEqual(settings.address, 'г. Москва, ул. Тестовая, д. 1')