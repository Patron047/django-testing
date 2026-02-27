from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Проверка доступности маршрутов проекта YaNote."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных один раз перед всеми тестами класса."""
        cls.author = User.objects.create(username='Автор Заметки')
        cls.reader = User.objects.create(username='Простой Читатель')
        cls.note = Note.objects.create(
            title='Заголовок тестовой заметки',
            text='Текст тестовой заметки.',
            slug='test-note-slug',
            author=cls.author,
        )
        cls.public_urls = (
            reverse('notes:home'),
            reverse('users:login'),
            reverse('users:signup'),
        )
        cls.private_urls = (
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:success'),
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.action_urls = (
            cls.detail_url,
            cls.edit_url,
            cls.delete_url,
        )
        cls.login_url = reverse('users:login')

    def test_public_pages_available_for_anonymous(self):
        """Главная, вход и регистрация доступны анонимному пользователю."""
        for url in self.public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_page_available(self):
        """Страница выхода доступна (принимает POST или GET)."""
        url = reverse('users:logout')
        response = self.client.post(url)
        self.assertIn(
            response.status_code,
            (HTTPStatus.OK, HTTPStatus.FOUND),
        )

    def test_private_pages_redirect_anonymous(self):
        """Аноним перенаправляется на логин."""
        urls_to_check = self.private_urls + self.action_urls

        for url in urls_to_check:
            with self.subTest(url=url):
                response = self.client.get(url)
                expected_url = f'{self.login_url}?next={url}'
                self.assertRedirects(response, expected_url)

    def test_auth_user_can_access_private_pages(self):
        """Авторизованный пользователь имеет доступ к списку и добавлению."""
        self.client.force_login(self.author)
        for url in self.private_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_can_access_note_actions(self):
        """Автор заметки может просматривать, редактировать и удалять её."""
        self.client.force_login(self.author)
        for url in self.action_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_other_user_cannot_access_note_actions(self):
        """Другой пользователь получает 404 при доступе к чужой заметке."""
        self.client.force_login(self.reader)
        for url in self.action_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
