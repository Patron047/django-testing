from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author(db):
    """Создаёт пользователя-автора."""
    return User.objects.create_user(
        username='Лев Толстой',
        password='password'
    )


@pytest.fixture
def reader(db):
    """Создаёт пользователя-читателя."""
    return User.objects.create_user(
        username='Читатель простой',
        password='password'
    )


@pytest.fixture
def news(db):
    """Создаёт тестовую новость."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(db, news, author):
    """Создаёт тестовый комментарий."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария для теста',
    )


@pytest.fixture
def author_client(author):
    """Клиент от имени автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Клиент от имени читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def home_url():
    """Возвращает URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    """Возвращает URL детальной страницы новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def login_url():
    """Возвращает URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def signup_url():
    """Возвращает URL страницы регистрации."""
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    """Возвращает URL выхода из системы."""
    return reverse('users:logout')


@pytest.fixture
def edit_url(comment):
    """Возвращает URL редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    """Возвращает URL удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def target_url(detail_url):
    """Возвращает целевой URL с якорем на комментарии."""
    return f'{detail_url}#comments'


@pytest.fixture
def redirect_edit_url(login_url, edit_url):
    """Возвращает URL редиректа для редактирования."""
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def redirect_delete_url(login_url, delete_url):
    """Возвращает URL редиректа для удаления."""
    return f'{login_url}?next={delete_url}'


@pytest.fixture
def many_news(db):
    """Создает набор новостей для проверки пагинации."""
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments(db, news, author):
    """Создаёт набор комментариев с разными датами."""
    now = timezone.now()
    comments_list = [
        Comment(news=news, author=author, text=f'Tекст {index}')
        for index in range(10)
    ]
    created_comments = Comment.objects.bulk_create(comments_list)
    for index, comment_item in enumerate(created_comments):
        comment_item.created = now + timedelta(days=index)
    Comment.objects.bulk_update(created_comments, ['created'])
    return created_comments
