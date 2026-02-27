import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
class TestHomePage:
    """Тесты контента главной страницы."""

    def test_news_count(self, client, many_news):
        """На главной странице не более 10 новостей."""
        url = reverse('news:home')
        response = client.get(url)
        object_list = response.context['object_list']
        assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, client, many_news):
        """Новости отсортированы по убыванию даты (новые сверху)."""
        url = reverse('news:home')
        response = client.get(url)
        object_list = response.context['object_list']
        dates = [news.date for news in object_list]
        sorted_dates = sorted(dates, reverse=True)
        assert dates == sorted_dates


@pytest.mark.django_db
class TestDetailPage:
    """Тесты контента страницы отдельной новости."""

    def test_comments_order(self, client, news_with_comments):
        """Комментарии отсортированы по времени создания (возрастание)."""
        news_item = news_with_comments['news']
        url = reverse('news:detail', args=(news_item.id,))
        response = client.get(url)
        news_obj = response.context['news']
        comments_qs = news_obj.comment_set.all()
        created_dates = [c.created for c in comments_qs]
        sorted_dates = sorted(created_dates)
        assert created_dates == sorted_dates

    def test_anonymous_has_no_form(self, client, news_with_comments):
        """Анонимный пользователь не видит форму комментария."""
        news_item = news_with_comments['news']
        url = reverse('news:detail', args=(news_item.id,))
        response = client.get(url)
        assert 'form' not in response.context

    def test_authorized_has_form(self, client, news_with_comments):
        """Авторизованный пользователь видит форму комментария."""
        news_item = news_with_comments['news']
        author = news_with_comments['author']
        url = reverse('news:detail', args=(news_item.id,))
        client.force_login(author)
        response = client.get(url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
