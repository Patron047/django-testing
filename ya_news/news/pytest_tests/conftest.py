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
        text='Текст комментария',
    )


@pytest.fixture
def comment_for_edit(db, news, author):
    """Создаёт комментарий для тестов редактирования и удаления."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Исходный текст',
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
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def edit_url(comment_for_edit):
    return reverse('news:edit', args=(comment_for_edit.id,))


@pytest.fixture
def delete_url(comment_for_edit):
    return reverse('news:delete', args=(comment_for_edit.id,))


@pytest.fixture
def target_url(news):
    return f"{reverse('news:detail', args=(news.id,))}#comments"


@pytest.fixture
def redirect_edit_url(login_url, edit_url):
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def redirect_delete_url(login_url, delete_url):
    return f'{login_url}?next={delete_url}'


@pytest.fixture
def many_news(db):
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
    now = timezone.now()
    result = []
    for index in range(10):
        comment_item = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment_item.created = now + timedelta(days=index)
        comment_item.save(update_fields=['created'])
        result.append(comment_item)
    return result
