import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db

URL_HOME = reverse('news:home')


@pytest.fixture
def detail_url(news):
    """Фикстура для URL страницы детали новости."""
    return reverse('news:detail', args=(news.id,))


def test_news_count(client, many_news):
    """На главной странице не более 10 новостей."""
    response = client.get(URL_HOME)
    news_items = response.context['object_list']
    assert news_items.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news):
    """Новости отсортированы по убыванию даты (новые сверху)."""
    response = client.get(URL_HOME)
    news_items = response.context['object_list']
    dates = [news.date for news in news_items]
    assert dates == sorted(dates, reverse=True)


def test_comments_order(client, news, comments, detail_url):
    """Комментарии отсортированы по времени создания (возрастание)."""
    response = client.get(detail_url)
    news_obj = response.context['news']
    created_dates = [c.created for c in news_obj.comment_set.all()]
    assert created_dates == sorted(created_dates)


def test_anonymous_has_no_form(client, news, detail_url):
    """Анонимный пользователь не видит форму комментария."""
    assert 'form' not in client.get(detail_url).context


def test_authorized_has_form(author_client, news, detail_url):
    """Авторизованный пользователь видит форму комментария."""
    response = author_client.get(detail_url)
    form = response.context.get('form')
    assert form is not None and isinstance(form, CommentForm)
