import pytest
from http import HTTPStatus

from django.urls import reverse

pytestmark = pytest.mark.django_db

URL_HOME = reverse('news:home')
URL_LOGIN = reverse('users:login')
URL_SIGNUP = reverse('users:signup')
URL_LOGOUT = reverse('users:logout')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def anon_redirect_urls(comment):
    """Словарь ожидаемых редиректов для анонима."""
    login = reverse('users:login')
    return {
        'edit': f"{login}?next={reverse('news:edit', args=(comment.id,))}",
        'delete': f"{login}?next={reverse('news:delete', args=(comment.id,))}",
    }


@pytest.mark.parametrize(
    'url_fixture_name,client_fixture_name,expected_status',
    [
        ('URL_HOME', 'client', HTTPStatus.OK),
        ('detail_url', 'client', HTTPStatus.OK),
        ('URL_LOGIN', 'client', HTTPStatus.OK),
        ('URL_SIGNUP', 'client', HTTPStatus.OK),
        ('edit_url', 'author_client', HTTPStatus.OK),
        ('edit_url', 'reader_client', HTTPStatus.NOT_FOUND),
        ('delete_url', 'author_client', HTTPStatus.OK),
        ('delete_url', 'reader_client', HTTPStatus.NOT_FOUND),
    ],
)
def test_pages_availability_and_permissions(
    request, url_fixture_name, client_fixture_name, expected_status
):
    """Единый тест для проверки статус-кодов всех страниц."""
    if url_fixture_name.startswith('URL_'):
        url = globals()[url_fixture_name]
    else:
        url = request.getfixturevalue(url_fixture_name)
    client = request.getfixturevalue(client_fixture_name)
    response = client.get(url)
    assert response.status_code == expected_status


def test_logout_page_availability(client):
    """Страница выхода доступна анониму."""
    response = client.get(URL_LOGOUT)
    allowed_statuses = (
        HTTPStatus.OK,
        HTTPStatus.FOUND,
        HTTPStatus.METHOD_NOT_ALLOWED,
    )
    assert response.status_code in allowed_statuses


@pytest.mark.parametrize(
    'url_fixture_name,redirect_key',
    [
        ('edit_url', 'edit'),
        ('delete_url', 'delete'),
    ],
)
def test_anonymous_redirect_on_comment_actions(
    request, client, url_fixture_name, redirect_key, anon_redirect_urls
):
    """Аноним перенаправляется на логин при действиях с комментарием."""
    url = request.getfixturevalue(url_fixture_name)
    expected_redirect = anon_redirect_urls[redirect_key]
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect
