from http import HTTPStatus

from notes.models import Note

from .base import BaseTestCase


class TestNoteLogic(BaseTestCase):
    """Тесты логики создания, редактирования и удаления заметок."""

    def test_anonymous_cant_create(self):
        """Аноним не может создать заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_to_add_anon)
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
        """Slug генерируется автоматически, если не передан."""
        form_data_copy = self.form_data.copy()
        form_data_copy.pop('slug')
        form_data_copy['title'] = 'Test Title For Slug'
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(self.add_url, data=form_data_copy)
        self.assertRedirects(response, self.success_url)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        new_ids = note_ids_after - note_ids_before
        self.assertEqual(len(new_ids), 1)
        new_id = new_ids.pop()
        created_note = Note.objects.get(id=new_id)
        self.assertEqual(created_note.title, form_data_copy['title'])
        self.assertEqual(created_note.text, form_data_copy['text'])
        self.assertEqual(created_note.author, self.author)
        expected_slug = form_data_copy['title'].lower().replace(' ', '-')
        self.assertEqual(created_note.slug, expected_slug)

    def test_create_note_with_duplicate_slug_fails(self):
        """Создание заметки с дублирующимся slug невозможно."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        form_data_copy = self.form_data.copy()
        form_data_copy['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, data=form_data_copy)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('slug', response.context['form'].errors)
        self.assertEqual(
            note_ids_before, set(Note.objects.values_list('id', flat=True))
        )

    def test_author_can_delete(self):
        """Автор может удалить свою заметку."""
        count_before = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        count_after = Note.objects.count()
        self.assertEqual(count_before - count_after, 1)

    def test_user_cannot_delete_foreign_note(self):
        """Пользователь не может удалить чужую заметку."""
        orig_title = self.note.title
        orig_text = self.note.text
        orig_slug = self.note.slug
        orig_author = self.note.author
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, orig_title)
        self.assertEqual(self.note.text, orig_text)
        self.assertEqual(self.note.slug, orig_slug)
        self.assertEqual(self.note.author, orig_author)

    def test_author_can_edit(self):
        """Автор может редактировать свою заметку."""
        form_data_copy = self.form_data.copy()
        form_data_copy['title'] = 'Edited Title'
        form_data_copy['text'] = 'Edited Text'
        form_data_copy['slug'] = 'edited-slug'
        response = self.author_client.post(self.edit_url, data=form_data_copy)
        self.assertRedirects(response, self.success_url)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, form_data_copy['title'])
        self.assertEqual(updated_note.text, form_data_copy['text'])
        self.assertEqual(updated_note.slug, form_data_copy['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_user_cannot_edit_foreign_note(self):
        """Пользователь не может редактировать чужую заметку."""
        orig_title = self.note.title
        orig_text = self.note.text
        orig_slug = self.note.slug
        orig_author = self.note.author
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, orig_title)
        self.assertEqual(self.note.text, orig_text)
        self.assertEqual(self.note.slug, orig_slug)
        self.assertEqual(self.note.author, orig_author)
