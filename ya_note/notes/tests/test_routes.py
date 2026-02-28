from .base import BaseTestCase


class TestRoutes(BaseTestCase):
    """Проверка доступности маршрутов проекта YaNote."""

    def test_status_codes_for_all_roles(self):
        """Проверка кодов возврата для всех ролей и страниц."""
        for url, client_method, expected_code in self.status_cases:
            with self.subTest(url=url, expected_code=expected_code):
                response = client_method(url)
                self.assertEqual(response.status_code, expected_code)

    def test_redirects_for_anonymous(self):
        """Перенаправления анонимного пользователя на страницу входа."""
        for url, expected_redirect in self.redirect_cases:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.anon_client.get(url),
                    expected_redirect,
                )
