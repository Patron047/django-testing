from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс с общими данными и URL для тестов маршрутов."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')

        cls.note = Note.objects.create(
            title='Test Note',
            text='Test Text',
            slug='test-note-slug',
            author=cls.author,
        )

        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.signup_url = reverse('users:signup')
        cls.logout_url = reverse('users:logout')
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.anon_client = Client()


class TestRoutes(BaseTestCase):
    """Проверка доступности маршрутов проекта YaNote."""

    def test_status_codes_for_all_roles(self):
        """Проверка кодов возврата для всех ролей и страниц."""
        cases = [
            (self.home_url, self.anon_client, HTTPStatus.OK, 'get'),
            (self.login_url, self.anon_client, HTTPStatus.OK, 'get'),
            (self.signup_url, self.anon_client, HTTPStatus.OK, 'get'),
            (self.logout_url, self.anon_client, HTTPStatus.OK, 'post'),
            (self.home_url, self.author_client, HTTPStatus.OK, 'get'),
            (self.login_url, self.author_client, HTTPStatus.OK, 'get'),
            (self.signup_url, self.author_client, HTTPStatus.OK, 'get'),
            (self.list_url, self.author_client, HTTPStatus.OK, 'get'),
            (self.add_url, self.author_client, HTTPStatus.OK, 'get'),
            (self.success_url, self.author_client, HTTPStatus.OK, 'get'),
            (self.detail_url, self.author_client, HTTPStatus.OK, 'get'),
            (self.edit_url, self.author_client, HTTPStatus.OK, 'get'),
            (self.delete_url, self.author_client, HTTPStatus.OK, 'get'),
            (self.detail_url, self.reader_client, HTTPStatus.NOT_FOUND, 'get'),
            (self.edit_url, self.reader_client, HTTPStatus.NOT_FOUND, 'get'),
            (self.delete_url, self.reader_client, HTTPStatus.NOT_FOUND, 'get'),
            (self.list_url, self.anon_client, HTTPStatus.FOUND, 'get'),
            (self.add_url, self.anon_client, HTTPStatus.FOUND, 'get'),
            (self.success_url, self.anon_client, HTTPStatus.FOUND, 'get'),
            (self.detail_url, self.anon_client, HTTPStatus.FOUND, 'get'),
            (self.edit_url, self.anon_client, HTTPStatus.FOUND, 'get'),
            (self.delete_url, self.anon_client, HTTPStatus.FOUND, 'get'),
        ]

        for url, client, expected_code, method in cases:
            with self.subTest(url=url,
                              client=client,
                              expected_code=expected_code
                              ):
                if method == 'post':
                    response = client.post(url)
                else:
                    response = client.get(url)
                self.assertEqual(response.status_code, expected_code)

    def test_redirects_for_anonymous(self):
        """Перенаправления анонимного пользователя на страницу входа."""
        urls_to_check = [
            self.list_url,
            self.add_url,
            self.success_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        ]

        for url in urls_to_check:
            with self.subTest(url=url):
                expected_redirect = f'{self.login_url}?next={url}'
                self.assertRedirects(
                    self.anon_client.get(url),
                    expected_redirect,
                )
