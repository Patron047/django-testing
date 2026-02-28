import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, many_news, home_url):
    """На главной странице не более 10 новостей."""
    assert client.get(home_url).context[
        'object_list'
    ].count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news, home_url):
    """Новости отсортированы по убыванию даты (новые сверху)."""
    dates = [
        news.date
        for news in client.get(home_url).context['object_list']
    ]
    assert dates == sorted(dates, reverse=True)


def test_comments_order(client, news, comments, detail_url):
    """Комментарии отсортированы по времени создания (возрастание)."""
    created_dates = [
        c.created
        for c in client.get(detail_url).context['news'].comment_set.all()
    ]
    assert created_dates == sorted(created_dates)


def test_anonymous_has_no_form(client, news, detail_url):
    """Анонимный пользователь не видит форму комментария."""
    assert 'form' not in client.get(detail_url).context


def test_authorized_has_form(author_client, news, detail_url):
    """Авторизованный пользователь видит форму комментария."""
    assert isinstance(
        author_client.get(detail_url).context.get('form'),
        CommentForm
    )
