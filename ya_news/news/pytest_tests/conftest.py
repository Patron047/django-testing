import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
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
def many_news(db):
    """Создаёт набор новостей для проверки главной страницы."""
    today = datetime.today()
    return News.objects.bulk_create([
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])


@pytest.fixture
def comments(db, news, author):
    """Создаёт набор комментариев для новости."""
    now = timezone.now()
    return Comment.objects.bulk_create([
        Comment(
            news=news,
            author=author,
            text=f'Tекст {index}',
            created=now + timedelta(days=index),
        )
        for index in range(10)
    ])
