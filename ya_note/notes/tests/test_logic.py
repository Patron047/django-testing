from http import HTTPStatus

from django.contrib.auth import get_user_model

from notes.models import Note
from .base import BaseTestCase

User = get_user_model()


class TestNoteLogic(BaseTestCase):
    """Тесты логики создания, редактирования и удаления заметок."""

    def test_anonymous_cant_create(self):
        """Аноним не может создать заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(self.add_url, data=self.form_data)
        expected_redirect = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(
            note_ids_before, set(Note.objects.values_list('id', flat=True))
        )

    def test_user_can_create(self):
        """Авторизованный пользователь создает заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        new_ids = note_ids_after - note_ids_before
        self.assertEqual(len(new_ids), 1)
        new_id = new_ids.pop()
        created_note = Note.objects.get(id=new_id)
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.slug, self.form_data['slug'])
        self.assertEqual(created_note.author, self.author)

    def test_slug_generated_if_missing(self):
        """Slug генерируется автоматически."""
        original_slug = self.form_data.get('slug')
        self.form_data.pop('slug')
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        new_ids = note_ids_after - note_ids_before
        self.assertEqual(len(new_ids), 1)
        new_id = new_ids.pop()
        created_note = Note.objects.get(id=new_id)
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.author, self.author)
        expected_slug = self.form_data['title'].lower().replace(' ', '-')
        self.assertEqual(created_note.slug, expected_slug)
        self.form_data['slug'] = original_slug

    def test_unique_slug_validation(self):
        """Проверка уникальности slug: ошибка при дубликате."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        original_slug = self.form_data.get('slug')
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.form_data['slug'] = original_slug
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('slug', response.context['form'].errors)
        self.assertEqual(
            note_ids_before, set(Note.objects.values_list('id', flat=True))
        )

    def test_author_can_delete(self):
        """Автор может удалить свою заметку."""
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_user_cant_delete_another(self):
        """Пользователь не может удалить чужую заметку."""
        note_before = Note.objects.get(id=self.note.id)
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_after = Note.objects.get(id=self.note.id)
        self.assertEqual(note_before, note_after)

    def test_author_can_edit(self):
        """Автор может редактировать свою заметку."""
        original_title = self.form_data.get('title')
        original_text = self.form_data.get('text')
        original_slug = self.form_data.get('slug')
        self.form_data['title'] = 'Edited Title'
        self.form_data['text'] = 'Edited Text'
        self.form_data['slug'] = 'edited-slug'
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.form_data['title'] = original_title
        self.form_data['text'] = original_text
        self.form_data['slug'] = original_slug
        self.assertRedirects(response, self.success_url)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, 'Edited Title')
        self.assertEqual(updated_note.text, 'Edited Text')
        self.assertEqual(updated_note.slug, 'edited-slug')
        self.assertEqual(updated_note.author, self.note.author)

    def test_user_cant_edit_another(self):
        """Пользователь не может редактировать чужую заметку."""
        note_before = Note.objects.get(id=self.note.id)
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_after = Note.objects.get(id=self.note.id)
        self.assertEqual(note_before, note_after)
