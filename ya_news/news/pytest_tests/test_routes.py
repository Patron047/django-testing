import pytest
from http import HTTPStatus
from pytest_lazyfixture import lazy_fixture

pytestmark = pytest.mark.django_db

STATUS_OK = HTTPStatus.OK
STATUS_FOUND = HTTPStatus.FOUND
STATUS_NOT_FOUND = HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_fixture,client_fixture,expected_status,method_name',
    [
        ('home_url', lazy_fixture('client'), STATUS_OK, 'get'),
        ('detail_url', lazy_fixture('client'), STATUS_OK, 'get'),
        ('login_url', lazy_fixture('client'), STATUS_OK, 'get'),
        ('signup_url', lazy_fixture('client'), STATUS_OK, 'get'),
        ('logout_url', lazy_fixture('client'), STATUS_OK, 'post'),
        ('edit_url', lazy_fixture('author_client'), STATUS_OK, 'get'),
        ('edit_url', lazy_fixture('reader_client'), STATUS_NOT_FOUND, 'get'),
        ('delete_url', lazy_fixture('author_client'), STATUS_OK, 'get'),
        ('delete_url', lazy_fixture('reader_client'), STATUS_NOT_FOUND, 'get'),
        ('edit_url', lazy_fixture('client'), STATUS_FOUND, 'get'),
        ('delete_url', lazy_fixture('client'), STATUS_FOUND, 'get'),
    ],
)
def test_all_routes_status_codes(
    request, url_fixture, client_fixture, expected_status, method_name
):
    """Единый тест для проверки статус-кодов всех страниц."""
    url = request.getfixturevalue(url_fixture)
    response = getattr(client_fixture, method_name)(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture,expected_redirect_fixture',
    [
        ('edit_url', 'redirect_edit_url'),
        ('delete_url', 'redirect_delete_url'),
    ],
)
def test_anonymous_redirect_urls(
    request, client, url_fixture, expected_redirect_fixture
):
    """Проверка конкретных URL редиректов для анонима."""
    url = request.getfixturevalue(url_fixture)
    expected_redirect = request.getfixturevalue(expected_redirect_fixture)
    response = client.get(url)
    assert response.status_code == STATUS_FOUND
    assert response.url == expected_redirect
