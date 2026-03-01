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
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Note 0',
            text='Text 0',
            slug='slug-0',
            author=cls.author,
        )
        cls.notes = [cls.note]
        cls.another_note = Note.objects.create(
            title='Foreign Note',
            text='Foreign Text',
            slug='foreign-slug',
            author=cls.reader,
        )
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
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
