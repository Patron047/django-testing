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
        self.assertEqual(note_ids_before,
                         set(Note.objects.values_list('id', flat=True))
                         )

    def test_user_can_create(self):
        """Авторизованный пользователь создает заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(len(note_ids_after), len(note_ids_before) + 1)
        new_id = (note_ids_after - note_ids_before).pop()
        created_note = Note.objects.get(id=new_id)
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.slug, self.form_data['slug'])
        self.assertEqual(created_note.author, self.author)

    def test_slug_generated_if_missing(self):
        """Slug генерируется автоматически."""
        data_no_slug = self.form_data.copy()
        data_no_slug.pop('slug')
        data_no_slug['title'] = 'Auto Slug Title'
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(self.add_url, data=data_no_slug)
        self.assertRedirects(response, self.success_url)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(len(note_ids_after), len(note_ids_before) + 1)
        new_id = (note_ids_after - note_ids_before).pop()
        created_note = Note.objects.get(id=new_id)
        self.assertEqual(created_note.title, data_no_slug['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.author, self.author)
        self.assertTrue(created_note.slug)

    def test_unique_slug_validation(self):
        """Проверка уникальности slug: ошибка при дубликате."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        form_with_duplicate = self.form_data.copy()
        form_with_duplicate['slug'] = self.note.slug
        response = self.author_client.post(self.add_url,
                                           data=form_with_duplicate
                                           )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('slug', response.context['form'].errors)
        self.assertEqual(note_ids_before,
                         set(Note.objects.values_list('id', flat=True))
                         )

    def test_author_can_delete(self):
        """Автор может удалить свою заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(len(note_ids_after), len(note_ids_before) - 1)
        self.assertNotIn(self.note.id, note_ids_after)

    def test_user_cant_delete_another(self):
        """Пользователь не может удалить чужую заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(note_ids_before, note_ids_after)
        current_note = Note.objects.get(id=self.note.id)
        self.assertEqual(current_note.title, 'Note 0')
        self.assertEqual(current_note.text, 'Text 0')
        self.assertEqual(current_note.slug, 'slug-0')
        self.assertEqual(current_note.author, self.author)

    def test_author_can_edit(self):
        """Автор может редактировать свою заметку."""
        edit_data = self.form_data.copy()
        edit_data['title'] = 'Edited Title'
        edit_data['text'] = 'Edited Text'
        edit_data['slug'] = 'edited-slug'
        response = self.author_client.post(self.edit_url, data=edit_data)
        self.assertRedirects(response, self.success_url)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, edit_data['title'])
        self.assertEqual(updated_note.text, edit_data['text'])
        self.assertEqual(updated_note.slug, edit_data['slug'])
        self.assertEqual(updated_note.author, self.author)

    def test_user_cant_edit_another(self):
        """Пользователь не может редактировать чужую заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(note_ids_before, note_ids_after)
        current_note = Note.objects.get(id=self.note.id)
        self.assertEqual(current_note.title, 'Note 0')
        self.assertEqual(current_note.text, 'Text 0')
        self.assertEqual(current_note.slug, 'slug-0')
        self.assertEqual(current_note.author, self.author)
