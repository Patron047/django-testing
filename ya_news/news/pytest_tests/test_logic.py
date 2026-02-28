import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

COMMENT_TEXT = 'Текст комментария'
NEW_TEXT = 'Обновлённый комментарий'
FORM_DATA = {'text': COMMENT_TEXT}
EDIT_DATA = {'text': NEW_TEXT}


@pytest.fixture
def detail_url(news):
    """URL страницы детали новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def delete_url(comment_for_edit):
    """URL удаления комментария."""
    return reverse('news:delete', args=(comment_for_edit.id,))


@pytest.fixture
def edit_url(comment_for_edit):
    """URL редактирования комментария."""
    return reverse('news:edit', args=(comment_for_edit.id,))


@pytest.fixture
def target_url(news):
    """Ожидаемый URL редиректа после действия с комментарием."""
    return f"{reverse('news:detail', args=(news.id,))}#comments"


def test_anonymous_cant_create(client, news, detail_url):
    """Анонимный пользователь не может создать комментарий."""
    count_before = Comment.objects.count()
    response = client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == count_before


def test_user_can_create(author_client, news, author, detail_url, target_url):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, target_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_bad_words_blocked(author_client, news, bad_word, detail_url):
    """Пользователь не может использовать стоп-слова в комментарии."""
    bad_text = f'Текст с плохим словом: {bad_word}'
    data = {'text': bad_text}
    response = author_client.post(detail_url, data=data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors
    assertFormError(
        response.context['form'],
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete(author_client,
                           comment_for_edit,
                           delete_url, target_url
                           ):
    """Автор может удалить свой комментарий."""
    response = author_client.delete(delete_url)
    assertRedirects(response, target_url)
    assert Comment.objects.count() == 0


def test_user_cant_delete_others(reader_client, comment_for_edit, delete_url):
    """Пользователь не может удалить чужой комментарий."""
    original_news = comment_for_edit.news
    original_author = comment_for_edit.author
    original_text = comment_for_edit.text
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    comment_for_edit.refresh_from_db()
    assert comment_for_edit.news == original_news
    assert comment_for_edit.author == original_author
    assert comment_for_edit.text == original_text


def test_author_can_edit(author_client,
                         comment_for_edit,
                         edit_url, target_url
                         ):
    """Автор может редактировать свой комментарий."""
    response = author_client.post(edit_url, data=EDIT_DATA)
    assertRedirects(response, target_url)
    updated_comment = Comment.objects.get(id=comment_for_edit.id)
    assert updated_comment.text == EDIT_DATA['text']
    assert updated_comment.news == comment_for_edit.news
    assert updated_comment.author == comment_for_edit.author


def test_user_cant_edit_others(reader_client, comment_for_edit, edit_url):
    """Пользователь не может редактировать чужой комментарий."""
    original_news = comment_for_edit.news
    original_author = comment_for_edit.author
    original_text = comment_for_edit.text
    response = reader_client.post(edit_url, data=EDIT_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    unchanged_comment = Comment.objects.get(id=comment_for_edit.id)
    assert unchanged_comment.news == original_news
    assert unchanged_comment.author == original_author
    assert unchanged_comment.text == original_text
