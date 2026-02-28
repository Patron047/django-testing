from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()

LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
HOME_URL = reverse('notes:home')


class BaseTestCase(TestCase):
    """Базовый класс для общих тестовых данных и клиентов."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')
        cls.other_user = User.objects.create(username='NotAuthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.anon_client = Client()
        cls.notes_count = 11
        notes_bulk = [
            Note(
                title=f'Note {i}',
                text=f'Text {i}',
                slug=f'slug-{i}',
                author=cls.author,
            )
            for i in range(cls.notes_count)
        ]
        cls.created_notes = Note.objects.bulk_create(notes_bulk)
        cls.notes = list(Note.objects.filter(author=cls.author).order_by('id'))
        cls.foreign_note = Note.objects.create(
            title='Foreign Note',
            text='Foreign Text',
            slug='foreign-slug',
            author=cls.other_user,
        )
        cls.note = cls.notes[0]
        note_slug = cls.note.slug
        cls.form_data = {
            'title': 'New Test Title',
            'text': 'New Test Text',
            'slug': 'new-test-slug',
        }
        cls.list_url = LIST_URL
        cls.add_url = ADD_URL
        cls.success_url = SUCCESS_URL
        cls.login_url = LOGIN_URL
        cls.logout_url = LOGOUT_URL
        cls.signup_url = SIGNUP_URL
        cls.home_url = HOME_URL
        cls.detail_url = reverse('notes:detail', args=(note_slug,))
        cls.edit_url = reverse('notes:edit', args=(note_slug,))
        cls.delete_url = reverse('notes:delete', args=(note_slug,))
        cls.status_cases = [
            (cls.home_url, cls.anon_client.get, HTTPStatus.OK),
            (cls.login_url, cls.anon_client.get, HTTPStatus.OK),
            (cls.signup_url, cls.anon_client.get, HTTPStatus.OK),
            (cls.logout_url, cls.anon_client.post, HTTPStatus.OK),
            (cls.home_url, cls.author_client.get, HTTPStatus.OK),
            (cls.login_url, cls.author_client.get, HTTPStatus.OK),
            (cls.signup_url, cls.author_client.get, HTTPStatus.OK),
            (cls.list_url, cls.author_client.get, HTTPStatus.OK),
            (cls.add_url, cls.author_client.get, HTTPStatus.OK),
            (cls.success_url, cls.author_client.get, HTTPStatus.OK),
            (cls.detail_url, cls.author_client.get, HTTPStatus.OK),
            (cls.edit_url, cls.author_client.get, HTTPStatus.OK),
            (cls.delete_url, cls.author_client.get, HTTPStatus.OK),
            (cls.detail_url, cls.reader_client.get, HTTPStatus.NOT_FOUND),
            (cls.edit_url, cls.reader_client.get, HTTPStatus.NOT_FOUND),
            (cls.delete_url, cls.reader_client.get, HTTPStatus.NOT_FOUND),
            (cls.list_url, cls.anon_client.get, HTTPStatus.FOUND),
            (cls.add_url, cls.anon_client.get, HTTPStatus.FOUND),
            (cls.success_url, cls.anon_client.get, HTTPStatus.FOUND),
            (cls.detail_url, cls.anon_client.get, HTTPStatus.FOUND),
            (cls.edit_url, cls.anon_client.get, HTTPStatus.FOUND),
            (cls.delete_url, cls.anon_client.get, HTTPStatus.FOUND),
        ]
        cls.redirect_cases = [
            (cls.list_url, f'{cls.login_url}?next={cls.list_url}'),
            (cls.add_url, f'{cls.login_url}?next={cls.add_url}'),
            (cls.success_url, f'{cls.login_url}?next={cls.success_url}'),
            (cls.detail_url, f'{cls.login_url}?next={cls.detail_url}'),
            (cls.edit_url, f'{cls.login_url}?next={cls.edit_url}'),
            (cls.delete_url, f'{cls.login_url}?next={cls.delete_url}'),
        ]
