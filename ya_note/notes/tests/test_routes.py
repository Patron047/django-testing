from http import HTTPStatus

from .base import (
    ADD_URL,
    DELETE_URL,
    DETAIL_URL,
    EDIT_URL,
    HOME_URL,
    LIST_URL,
    LOGIN_URL,
    LOGOUT_URL,
    REDIRECT_TO_ADD,
    REDIRECT_TO_DELETE,
    REDIRECT_TO_DETAIL,
    REDIRECT_TO_EDIT,
    REDIRECT_TO_LIST,
    REDIRECT_TO_SUCCESS,
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
            (DETAIL_URL, self.author_client, 'get', HTTPStatus.OK),
            (EDIT_URL, self.author_client, 'get', HTTPStatus.OK),
            (DELETE_URL, self.author_client, 'get', HTTPStatus.OK),
            (DETAIL_URL, self.reader_client, 'get', HTTPStatus.NOT_FOUND),
            (EDIT_URL, self.reader_client, 'get', HTTPStatus.NOT_FOUND),
            (DELETE_URL, self.reader_client, 'get', HTTPStatus.NOT_FOUND),
            (LIST_URL, self.client, 'get', HTTPStatus.FOUND),
            (ADD_URL, self.client, 'get', HTTPStatus.FOUND),
            (SUCCESS_URL, self.client, 'get', HTTPStatus.FOUND),
            (DETAIL_URL, self.client, 'get', HTTPStatus.FOUND),
            (EDIT_URL, self.client, 'get', HTTPStatus.FOUND),
            (DELETE_URL, self.client, 'get', HTTPStatus.FOUND),
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
            (LIST_URL, REDIRECT_TO_LIST),
            (ADD_URL, REDIRECT_TO_ADD),
            (SUCCESS_URL, REDIRECT_TO_SUCCESS),
            (DETAIL_URL, REDIRECT_TO_DETAIL),
            (EDIT_URL, REDIRECT_TO_EDIT),
            (DELETE_URL, REDIRECT_TO_DELETE),
        ]
        for url, expected_redirect in redirect_cases:
            with self.subTest(url=url, client=self.client):
                self.assertRedirects(
                    self.client.get(url),
                    expected_redirect,
                )
