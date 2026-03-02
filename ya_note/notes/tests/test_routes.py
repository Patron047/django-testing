from http import HTTPStatus

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

    def test_status_codes_for_all_roles(self):
        """Проверка кодов возврата для всех ролей и страниц."""
        status_cases = [
            (HOME_URL, self.client, 'get', HTTPStatus.OK),
            (LOGIN_URL, self.client, 'get', HTTPStatus.OK),
            (SIGNUP_URL, self.client, 'get', HTTPStatus.OK),
            (LOGOUT_URL, self.client, 'post', HTTPStatus.OK),
            (HOME_URL, self.author_client, 'get', HTTPStatus.OK),
            (LOGIN_URL, self.author_client, 'get', HTTPStatus.OK),
            (SIGNUP_URL, self.author_client, 'get', HTTPStatus.OK),
            (LIST_URL, self.author_client, 'get', HTTPStatus.OK),
            (ADD_URL, self.author_client, 'get', HTTPStatus.OK),
            (SUCCESS_URL, self.author_client, 'get', HTTPStatus.OK),
            (self.detail_url, self.author_client, 'get', HTTPStatus.OK),
            (self.edit_url, self.author_client, 'get', HTTPStatus.OK),
            (self.delete_url, self.author_client, 'get', HTTPStatus.OK),
            (self.detail_url, self.reader_client, 'get', HTTPStatus.NOT_FOUND),
            (self.edit_url, self.reader_client, 'get', HTTPStatus.NOT_FOUND),
            (self.delete_url, self.reader_client, 'get', HTTPStatus.NOT_FOUND),
            (LIST_URL, self.client, 'get', HTTPStatus.FOUND),
            (ADD_URL, self.client, 'get', HTTPStatus.FOUND),
            (SUCCESS_URL, self.client, 'get', HTTPStatus.FOUND),
            (self.detail_url, self.client, 'get', HTTPStatus.FOUND),
            (self.edit_url, self.client, 'get', HTTPStatus.FOUND),
            (self.delete_url, self.client, 'get', HTTPStatus.FOUND),
        ]
        for url, client, method, expected_code in status_cases:
            with self.subTest(url=url,
                              client=client,
                              expected_code=expected_code
                              ):
                response = getattr(client, method)(url)
                self.assertEqual(response.status_code, expected_code)

    def test_redirects_for_anonymous(self):
        """Перенаправления анонимного пользователя на страницу входа."""
        redirect_cases = [
            (LIST_URL, self.redirect_to_list),
            (ADD_URL, self.redirect_to_add),
            (SUCCESS_URL, self.redirect_to_success),
            (self.detail_url, self.redirect_to_detail),
            (self.edit_url, self.redirect_to_edit),
            (self.delete_url, self.redirect_to_delete),
        ]
        for url, expected_redirect in redirect_cases:
            with self.subTest(url=url, client=self.client):
                self.assertRedirects(
                    self.client.get(url),
                    expected_redirect,
                )
