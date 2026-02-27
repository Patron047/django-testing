from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты создания заметок согласно ТЗ."""

    NOTE_TITLE = 'Test Title'
    NOTE_TEXT = 'Test Text'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='User')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
        }
        cls.create_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')

    def test_anonymous_cant_create(self):
        """Анонимный пользователь не может создать заметку."""
        count_before = Note.objects.count()
        response = self.client.post(self.create_url, data=self.form_data)
        expected_redirect = f'{self.login_url}?next={self.create_url}'
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(Note.objects.count(), count_before)

    def test_user_can_create(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.auth_client.post(self.create_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.author, self.user)
        self.assertTrue(note.slug)

    def test_slug_generated_if_missing(self):
        """Если slug не заполнен, он формируется автоматически."""
        data = {'title': 'New Title', 'text': 'Text'}
        response = self.auth_client.post(self.create_url, data=data)
        self.assertRedirects(response, self.success_url)
        note = Note.objects.get(title='New Title')
        self.assertTrue(note.slug)
        self.assertTrue(note.slug.isascii())
        self.assertFalse(' ' in note.slug)

    def test_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        Note.objects.create(
            title=self.NOTE_TITLE,
            text='First',
            author=self.user,
            slug='same-slug'
        )
        response = self.auth_client.post(self.create_url, data=self.form_data)
        notes_with_same_title = Note.objects.filter(title=self.NOTE_TITLE)
        if response.status_code == HTTPStatus.FOUND:
            self.assertEqual(notes_with_same_title.count(), 2)
            slugs = [n.slug for n in notes_with_same_title]
            self.assertNotEqual(slugs[0], slugs[1])
        else:
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn('slug', response.context['form'].errors)


class TestNoteEditDelete(TestCase):
    """Тесты редактирования и удаления согласно ТЗ."""

    NOTE_TITLE = 'Editable Note'
    NEW_TITLE = 'Updated Title'
    NOTE_TEXT = 'Original Text'
    NEW_TEXT = 'Updated Text'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug='editable-note'
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
        }

    def test_author_can_delete(self):
        """Автор может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_another(self):
        """Пользователь не может удалить чужую заметку."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_user_cant_edit_another(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
