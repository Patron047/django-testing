import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
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
def setup_data(author, reader, news, comment):
    """Собирает основные объекты для тестов маршрутов в словарь."""
    return {
        'author': author,
        'reader': reader,
        'news': news,
        'comment': comment,
    }


@pytest.fixture
def author_client(client, author):
    """Клиент от имени автора."""
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(client, reader):
    """Клиент от имени читателя."""
    client.force_login(reader)
    return client


@pytest.fixture
def many_news(db):
    """Создаёт набор новостей для проверки главной страницы."""
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(news_list)


@pytest.fixture
def news_with_comments(db, author):
    """Создаёт новость с набором комментариев."""
    news_item = News.objects.create(
        title='Тестовая новость',
        text='Просто текст.'
    )
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news_item,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)

    return {
        'news': news_item,
        'comments': comments,
        'author': author,
    }


@pytest.fixture
def home_data(many_news):
    """Фикстура для главной страницы."""
    return {'news_list': many_news}


@pytest.fixture
def detail_data(news_with_comments):
    return news_with_comments
