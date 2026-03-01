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


@pytest.mark.parametrize(
    'url_fixture,client_fixture,expected_status,method_name',
    [
        ('home_url', ANONYMOUS_CLIENT, STATUS_OK, 'get'),
        ('detail_url', ANONYMOUS_CLIENT, STATUS_OK, 'get'),
        ('login_url', ANONYMOUS_CLIENT, STATUS_OK, 'get'),
        ('signup_url', ANONYMOUS_CLIENT, STATUS_OK, 'get'),
        ('logout_url', ANONYMOUS_CLIENT, STATUS_OK, 'post'),
        ('edit_url', AUTHOR_CLIENT, STATUS_OK, 'get'),
        ('edit_url', READER_CLIENT, STATUS_NOT_FOUND, 'get'),
        ('delete_url', AUTHOR_CLIENT, STATUS_OK, 'get'),
        ('delete_url', READER_CLIENT, STATUS_NOT_FOUND, 'get'),
        ('edit_url', ANONYMOUS_CLIENT, STATUS_FOUND, 'get'),
        ('delete_url', ANONYMOUS_CLIENT, STATUS_FOUND, 'get'),
    ],
)
def test_all_routes_status_codes(
    request, url_fixture, client_fixture, expected_status, method_name
):
    """Единый тест для проверки статус-кодов всех страниц."""
    response = getattr(client_fixture, method_name)(
        request.getfixturevalue(url_fixture)
    )
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture,expected_redirect_fixture',
    [
        (lazy_fixture('edit_url'), lazy_fixture('redirect_edit_url')),
        (lazy_fixture('delete_url'), lazy_fixture('redirect_delete_url')),
    ],
)
def test_anonymous_redirect_urls(
    client, url_fixture, expected_redirect_fixture
):
    """Проверка конкретных URL редиректов для анонима."""
    response = client.get(url_fixture)
    assert response.url == expected_redirect_fixture
