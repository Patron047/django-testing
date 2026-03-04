from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Текст тестового комментария'}

BAD_WORD_TEST_DATA = [
    {'text': f'Текст с плохим словом: {word}'}
    for word in BAD_WORDS
]


def test_anonymous_cant_create(client, detail_url):
    """Анонимный пользователь не может создать комментарий."""
    response = client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_can_create(
    author_client, news, author, detail_url, target_url
):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, target_url)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_data', BAD_WORD_TEST_DATA)
def test_bad_words_blocked(author_client, bad_data, detail_url):
    """Пользователь не может использовать стоп-слова в комментарии."""
    response = author_client.post(detail_url, data=bad_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors
    assertFormError(
        response.context['form'], field='text', errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete(
    author_client, comment, delete_url, target_url
):
    """Автор может удалить свой комментарий."""
    response = author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, target_url)
    assert Comment.objects.count() == 0


def test_user_cant_delete_others(
    reader_client, comment, delete_url
):
    """Пользователь не может удалить чужой комментарий."""
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == comment.text
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author


def test_author_can_edit(
    author_client, comment, edit_url, target_url
):
    """Автор может редактировать свой комментарий."""
    FORM_DATA['text'] = 'Обновлённый комментарий'
    response = author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, target_url)
    updated = Comment.objects.get(id=comment.id)
    assert updated.text == FORM_DATA['text']


def test_user_cant_edit_others(
    reader_client, comment, edit_url
):
    """Пользователь не может редактировать чужой комментарий."""
    original_text = comment.text
    FORM_DATA['text'] = 'Обновлённый комментарий'
    response = reader_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == original_text
