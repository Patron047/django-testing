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
        cls.form_data = {
            'title': 'Edited Title',
            'text': 'Edited Text',
            'slug': 'edited-slug',
        }
