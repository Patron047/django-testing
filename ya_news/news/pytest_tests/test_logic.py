import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


class TestCommentCreation:
    """Тесты создания комментариев."""

    COMMENT_TEXT = 'Текст комментария'

    def test_anonymous_cant_create(self, client, news):
        """Анонимный пользователь не может создать комментарий."""
        url = reverse('news:detail', args=(news.id,))
        data = {'text': self.COMMENT_TEXT}
        count_before = Comment.objects.count()
        client.post(url, data=data)
        assert Comment.objects.count() == count_before

    def test_user_can_create(
        self, author_client, news, author
    ):
        """Авторизованный пользователь может создать комментарий."""
        url = reverse('news:detail', args=(news.id,))
        data = {'text': self.COMMENT_TEXT}
        response = author_client.post(url, data=data)
        expected_url = f'{url}#comments'
        assertRedirects(response, expected_url)
        assert Comment.objects.count() == 1
        comment = Comment.objects.get()
        assert comment.text == self.COMMENT_TEXT
        assert comment.news == news
        assert comment.author == author

    def test_bad_words_blocked(self, author_client, news):
        """Пользователь не может использовать стоп-слова в комментарии."""
        url = reverse('news:detail', args=(news.id,))
        bad_text = f'Текст с плохим словом: {BAD_WORDS[0]}'
        data = {'text': bad_text}
        response = author_client.post(url, data=data)
        assert response.context['form'].errors
        assertFormError(
            response.context['form'],
            field='text',
            errors=WARNING
        )
        assert Comment.objects.count() == 0


class TestCommentEditDelete:
    """Тесты редактирования и удаления комментариев."""

    NEW_TEXT = 'Обновлённый комментарий'

    @pytest.fixture
    def comment(self, db, news, author):
        """Создаёт комментарий для тестов."""
        return Comment.objects.create(
            news=news,
            author=author,
            text='Исходный текст',
        )

    def test_author_can_delete(
        self, author_client, comment, news
    ):
        """Автор может удалить свой комментарий."""
        url = reverse('news:delete', args=(comment.id,))
        target_url = f"{reverse('news:detail', args=(news.id,))}#comments"
        response = author_client.delete(url)
        assertRedirects(response, target_url)
        assert Comment.objects.count() == 0

    def test_user_cant_delete_others(
        self, reader_client, comment
    ):
        """Пользователь не может удалить чужой комментарий."""
        url = reverse('news:delete', args=(comment.id,))
        count_before = Comment.objects.count()
        response = reader_client.delete(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Comment.objects.count() == count_before

    def test_author_can_edit(
        self, author_client, comment, news
    ):
        """Автор может редактировать свой комментарий."""
        url = reverse('news:edit', args=(comment.id,))
        target_url = f"{reverse('news:detail', args=(news.id,))}#comments"
        data = {'text': self.NEW_TEXT}
        response = author_client.post(url, data=data)
        assertRedirects(response, target_url)
        comment.refresh_from_db()
        assert comment.text == self.NEW_TEXT

    def test_user_cant_edit_others(
        self, reader_client, comment
    ):
        """Пользователь не может редактировать чужой комментарий."""
        url = reverse('news:edit', args=(comment.id,))
        data = {'text': self.NEW_TEXT}
        original_text = comment.text
        response = reader_client.post(url, data=data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        comment.refresh_from_db()
        assert comment.text == original_text
