from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture

pytestmark = pytest.mark.django_db

STATUS_OK = HTTPStatus.OK
STATUS_FOUND = HTTPStatus.FOUND
STATUS_NOT_FOUND = HTTPStatus.NOT_FOUND
ANONYMOUS_CLIENT = lazy_fixture('client')
AUTHOR_CLIENT = lazy_fixture('author_client')
READER_CLIENT = lazy_fixture('reader_client')
HOME_URL = lazy_fixture('home_url')
DETAIL_URL = lazy_fixture('detail_url')
LOGIN_URL = lazy_fixture('login_url')
SIGNUP_URL = lazy_fixture('signup_url')
LOGOUT_URL = lazy_fixture('logout_url')
EDIT_URL = lazy_fixture('edit_url')
DELETE_URL = lazy_fixture('delete_url')
REDIRECT_EDIT_URL = lazy_fixture('redirect_edit_url')
REDIRECT_DELETE_URL = lazy_fixture('redirect_delete_url')


@pytest.mark.parametrize(
    'url_fixture,client_fixture,expected_status,method_name',
    [
        (HOME_URL, ANONYMOUS_CLIENT, STATUS_OK, 'get'),
        (DETAIL_URL, ANONYMOUS_CLIENT, STATUS_OK, 'get'),
        (LOGIN_URL, ANONYMOUS_CLIENT, STATUS_OK, 'get'),
        (SIGNUP_URL, ANONYMOUS_CLIENT, STATUS_OK, 'get'),
        (LOGOUT_URL, ANONYMOUS_CLIENT, STATUS_OK, 'post'),
        (EDIT_URL, AUTHOR_CLIENT, STATUS_OK, 'get'),
        (EDIT_URL, READER_CLIENT, STATUS_NOT_FOUND, 'get'),
        (DELETE_URL, AUTHOR_CLIENT, STATUS_OK, 'get'),
        (DELETE_URL, READER_CLIENT, STATUS_NOT_FOUND, 'get'),
        (EDIT_URL, ANONYMOUS_CLIENT, STATUS_FOUND, 'get'),
        (DELETE_URL, ANONYMOUS_CLIENT, STATUS_FOUND, 'get'),
    ],
)
def test_all_routes_status_codes(
    url_fixture, client_fixture, expected_status, method_name
):
    """Единый тест для проверки статус-кодов всех страниц."""
    response = getattr(client_fixture, method_name)(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture,expected_redirect_fixture',
    [
        (EDIT_URL, REDIRECT_EDIT_URL),
        (DELETE_URL, REDIRECT_DELETE_URL),
    ],
)
def test_anonymous_redirect_urls(
    client, url_fixture, expected_redirect_fixture
):
    """Проверка конкретных URL редиректов для анонима."""
    response = client.get(url_fixture)
    assert response.url == expected_redirect_fixture
