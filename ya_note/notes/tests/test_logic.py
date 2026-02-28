from http import HTTPStatus

from django.contrib.auth import get_user_model

from .base import BaseTestCase
from notes.models import Note

User = get_user_model()


class TestNoteLogic(BaseTestCase):
    """Тесты логики создания, редактирования и удаления заметок."""

    def test_anonymous_cant_create(self):
        """Аноним не может создать заметку."""
        count_before = Note.objects.count()
        response = self.anon_client.post(self.add_url, data=self.form_data)
        expected_redirect = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(Note.objects.count(), count_before)

    def test_user_can_create(self):
        """Авторизованный пользователь создает заметку."""
        count_before = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), count_before + 1)
        created_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.author, self.author)

    def test_slug_generated_if_missing(self):
        """Slug генерируется автоматически."""
        data_no_slug = self.form_data.copy()
        data_no_slug.pop('slug')
        data_no_slug['title'] = 'Auto Slug Title'
        count_before = Note.objects.count()
        response = self.author_client.post(self.add_url, data=data_no_slug)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), count_before + 1)
        created_note = Note.objects.get(title='Auto Slug Title')
        self.assertTrue(created_note.slug)
        self.assertTrue(created_note.slug.isascii())
        self.assertNotIn(' ', created_note.slug)

    def test_unique_slug_validation(self):
        """Проверка уникальности slug: ошибка при дубликате."""
        duplicate_slug = self.form_data['slug']
        Note.objects.create(
            title='Existing',
            text='Existing Text',
            slug=duplicate_slug,
            author=self.author,
        )
        count_before = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('slug', response.context['form'].errors)
        self.assertEqual(Note.objects.count(), count_before)

    def test_author_can_delete(self):
        """Автор может удалить свою заметку."""
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        count_before = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), count_before - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_user_cant_delete_another(self):
        """Пользователь не может удалить чужую заметку."""
        count_before = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), count_before)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Note 0')
        self.assertEqual(self.note.text, 'Text 0')

    def test_author_can_edit(self):
        """Автор может редактировать свою заметку."""
        edit_data = self.form_data.copy()
        edit_data['title'] = 'Edited Title'
        edit_data['text'] = 'Edited Text'
        edit_data['slug'] = 'edited-slug'
        response = self.author_client.post(self.edit_url, data=edit_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Edited Title')
        self.assertEqual(self.note.text, 'Edited Text')
        self.assertEqual(self.note.slug, 'edited-slug')
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_edit_another(self):
        """Пользователь не может редактировать чужую заметку."""
        original_title = self.note.title
        original_text = self.note.text
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, original_title)
        self.assertEqual(self.note.text, original_text)
