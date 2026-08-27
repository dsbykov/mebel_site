from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Project, ProjectImage


class ProjectImageInlineAdminTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='portfolio-admin',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(self.user)
        self.project = Project.objects.create(title='Проект с фотографией')
        self.project_image = ProjectImage.objects.create(
            project=self.project,
            image='portfolio/existing.webp',
            alt_text='Существующая фотография',
        )

    def test_project_page_has_visible_image_delete_control(self):
        response = self.client.get(
            reverse('admin:my_site_project_change', args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin-project-image-preview')
        self.assertContains(response, 'name="images-0-DELETE"')
        self.assertContains(response, 'Удалить')
