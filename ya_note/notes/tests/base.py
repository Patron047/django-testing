from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTE_SLUG = 'slug-0'

LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
HOME_URL = reverse('notes:home')

DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))

REDIRECT_TO_LIST = f'{LOGIN_URL}?next={LIST_URL}'
REDIRECT_TO_ADD = f'{LOGIN_URL}?next={ADD_URL}'
REDIRECT_TO_SUCCESS = f'{LOGIN_URL}?next={SUCCESS_URL}'
REDIRECT_TO_DETAIL = f'{LOGIN_URL}?next={DETAIL_URL}'
REDIRECT_TO_EDIT = f'{LOGIN_URL}?next={EDIT_URL}'
REDIRECT_TO_DELETE = f'{LOGIN_URL}?next={DELETE_URL}'
REDIRECT_TO_ADD_ANON = REDIRECT_TO_ADD
REDIRECT_TO_EDIT_ANON = REDIRECT_TO_EDIT
REDIRECT_TO_DELETE_ANON = REDIRECT_TO_DELETE


class BaseTestCase(TestCase):
    """Базовый класс для общих тестовых данных и клиентов."""

    @classmethod
    def setUpTestData(cls):
        """Инициализация тестовых данных: пользователи, клиенты и заметки."""
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Note 0',
            text='Text 0',
            slug=NOTE_SLUG,
            author=cls.author,
        )
        cls.foreign_note = Note.objects.create(
            title='Foreign Note',
            text='Foreign Text',
            slug='foreign-slug',
            author=cls.reader,
        )

        cls.form_data = {
            'title': 'Новый тестовый заголовок',
            'text': 'New Test Text',
            'slug': 'new-test-slug',
        }
        cls.add_url = ADD_URL
        cls.success_url = SUCCESS_URL
        cls.login_url = LOGIN_URL
        cls.detail_url = DETAIL_URL
        cls.edit_url = EDIT_URL
        cls.delete_url = DELETE_URL
        cls.redirect_to_list = REDIRECT_TO_LIST
        cls.redirect_to_add = REDIRECT_TO_ADD
        cls.redirect_to_success = REDIRECT_TO_SUCCESS
        cls.redirect_to_detail = REDIRECT_TO_DETAIL
        cls.redirect_to_edit = REDIRECT_TO_EDIT
        cls.redirect_to_delete = REDIRECT_TO_DELETE
        cls.redirect_to_add_anon = REDIRECT_TO_ADD_ANON
        cls.redirect_to_edit_anon = REDIRECT_TO_EDIT_ANON
        cls.redirect_to_delete_anon = REDIRECT_TO_DELETE_ANON
