import pytest
from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name,args_key',
    (
        ('news:home', None),
        ('news:detail', 'news'),
        ('users:login', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, setup_data, name, args_key):
    """Главная, новость, вход и регистрация доступны анониму (статус 200)."""
    if args_key:
        obj = setup_data[args_key]
        url = reverse(name, args=(obj.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_logout_page_availability(client):
    """Страница выхода доступна анониму."""
    url = reverse('users:logout')
    response = client.get(url)
    allowed_statuses = (
        HTTPStatus.OK,
        HTTPStatus.FOUND,
        HTTPStatus.METHOD_NOT_ALLOWED,
    )
    assert response.status_code in allowed_statuses, (
        f"Страница выхода вернула статус {response.status_code}, "
        f"ожидался один из: {allowed_statuses}"
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_key,expected_status',
    (
        ('author', HTTPStatus.OK),
        ('reader', HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'url_name',
    ('news:edit', 'news:delete')
)
def test_comment_edit_delete_permissions(
    client, setup_data, user_key, expected_status, url_name
):
    """
    Автор может редактировать/удалять комментарий.
    Другой пользователь получает ошибку 404.
    """
    user = setup_data[user_key]
    comment = setup_data['comment']
    client.force_login(user)
    url = reverse(url_name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name',
    ('news:edit', 'news:delete')
)
def test_anonymous_redirect_on_comment_actions(
    client, setup_data, url_name
):
    """
    Анонимный пользователь перенаправляется на страницу логина
    при попытке редактировать или удалить комментарий.
    """
    comment = setup_data['comment']
    login_url = reverse('users:login')
    url = reverse(url_name, args=(comment.id,))
    expected_redirect = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect
