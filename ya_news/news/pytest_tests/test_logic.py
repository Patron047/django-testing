import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

COMMENT_TEXT = 'Текст комментария'
NEW_TEXT = 'Обновлённый комментарий'
FORM_DATA = {'text': COMMENT_TEXT}

BAD_WORDTestData = [
    {'text': f'Текст с плохим словом: {word}'}
    for word in BAD_WORDS
]


def test_anonymous_cant_create(client, detail_url):
    """Анонимный пользователь не может создать комментарий."""
    client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == 0


def test_user_can_create(author_client, news, author, detail_url, target_url):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, target_url)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_data', BAD_WORDTestData)
def test_bad_words_blocked(author_client, bad_data, detail_url):
    """Пользователь не может использовать стоп-слова в комментарии."""
    response = author_client.post(detail_url, data=bad_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors
    assertFormError(
        response.context['form'], field='text', errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete(author_client,
                           comment_for_edit,
                           delete_url,
                           target_url):
    """Автор может удалить свой комментарий."""
    response = author_client.delete(delete_url)
    assertRedirects(response, target_url)
    assert Comment.objects.count() == 0


def test_user_cant_delete_others(reader_client, comment_for_edit, delete_url):
    """Пользователь не может удалить чужой комментарий."""
    assert Comment.objects.count() == 1
    reader_client.delete(delete_url)
    comment = Comment.objects.get(id=comment_for_edit.id)
    assert comment.news == comment_for_edit.news
    assert comment.author == comment_for_edit.author
    assert comment.text == comment_for_edit.text
    assert Comment.objects.count() == 1


def test_author_can_edit(
    author_client, comment_for_edit, edit_url, target_url
):
    """Автор может редактировать свой комментарий."""
    response = author_client.post(edit_url, data={'text': NEW_TEXT})
    assertRedirects(response, target_url)
    updated = Comment.objects.get(id=comment_for_edit.id)
    assert updated.text == NEW_TEXT
    assert updated.news == comment_for_edit.news
    assert updated.author == comment_for_edit.author


def test_user_cant_edit_others(reader_client, comment_for_edit, edit_url):
    """Пользователь не может редактировать чужой комментарий."""
    reader_client.post(edit_url, data={'text': NEW_TEXT})
    comment = Comment.objects.get(id=comment_for_edit.id)
    assert comment.news == comment_for_edit.news
    assert comment.author == comment_for_edit.author
    assert comment.text == comment_for_edit.text
