from http import HTTPStatus

from django.urls import reverse

from .base import (
    ADD_URL,
    HOME_URL,
    LIST_URL,
    LOGIN_URL,
    LOGOUT_URL,
    SIGNUP_URL,
    SUCCESS_URL,
    BaseTestCase,
)


class TestRoutes(BaseTestCase):
    """Проверка доступности маршрутов проекта YaNote."""

    def _get_client(self, role):
        if role == 'anon':
            return self.client
        if role == 'author':
            return self.author_client
        if role == 'reader':
            return self.reader_client
        raise ValueError(f"Unknown role: {role}")

    def test_status_codes_for_all_roles(self):
        """Проверка кодов возврата для всех ролей и страниц."""
        note_slug = self.note.slug
        detail_url = reverse('notes:detail', args=(note_slug,))
        edit_url = reverse('notes:edit', args=(note_slug,))
        delete_url = reverse('notes:delete', args=(note_slug,))
        status_cases = [
            (HOME_URL, 'anon', 'get', HTTPStatus.OK),
            (LOGIN_URL, 'anon', 'get', HTTPStatus.OK),
            (SIGNUP_URL, 'anon', 'get', HTTPStatus.OK),
            (LOGOUT_URL, 'anon', 'post', HTTPStatus.OK),
            (HOME_URL, 'author', 'get', HTTPStatus.OK),
            (LOGIN_URL, 'author', 'get', HTTPStatus.OK),
            (SIGNUP_URL, 'author', 'get', HTTPStatus.OK),
            (LIST_URL, 'author', 'get', HTTPStatus.OK),
            (ADD_URL, 'author', 'get', HTTPStatus.OK),
            (SUCCESS_URL, 'author', 'get', HTTPStatus.OK),
            (detail_url, 'author', 'get', HTTPStatus.OK),
            (edit_url, 'author', 'get', HTTPStatus.OK),
            (delete_url, 'author', 'get', HTTPStatus.OK),
            (detail_url, 'reader', 'get', HTTPStatus.NOT_FOUND),
            (edit_url, 'reader', 'get', HTTPStatus.NOT_FOUND),
            (delete_url, 'reader', 'get', HTTPStatus.NOT_FOUND),
            (LIST_URL, 'anon', 'get', HTTPStatus.FOUND),
            (ADD_URL, 'anon', 'get', HTTPStatus.FOUND),
            (SUCCESS_URL, 'anon', 'get', HTTPStatus.FOUND),
            (detail_url, 'anon', 'get', HTTPStatus.FOUND),
            (edit_url, 'anon', 'get', HTTPStatus.FOUND),
            (delete_url, 'anon', 'get', HTTPStatus.FOUND),
        ]
        for url, role, method, expected_code in status_cases:
            with self.subTest(url=url, expected_code=expected_code):
                client = self._get_client(role)
                response = getattr(client, method)(url)
                self.assertEqual(response.status_code, expected_code)

    def test_redirects_for_anonymous(self):
        """Перенаправления анонимного пользователя на страницу входа."""
        note_slug = self.note.slug
        detail_url = reverse('notes:detail', args=(note_slug,))
        edit_url = reverse('notes:edit', args=(note_slug,))
        delete_url = reverse('notes:delete', args=(note_slug,))
        redirect_cases = [
            (LIST_URL, f'{LOGIN_URL}?next={LIST_URL}'),
            (ADD_URL, f'{LOGIN_URL}?next={ADD_URL}'),
            (SUCCESS_URL, f'{LOGIN_URL}?next={SUCCESS_URL}'),
            (detail_url, f'{LOGIN_URL}?next={detail_url}'),
            (edit_url, f'{LOGIN_URL}?next={edit_url}'),
            (delete_url, f'{LOGIN_URL}?next={delete_url}'),
        ]
        for url, expected_redirect in redirect_cases:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    expected_redirect,
                )
