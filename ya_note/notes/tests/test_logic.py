from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс с общими данными и URL для всех тестов логики."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')
        cls.other_user = User.objects.create(username='Other')
        cls.note = Note.objects.create(
            title='Initial Title',
            text='Initial Text',
            slug='initial-slug',
            author=cls.author,
        )
        cls.other_note = Note.objects.create(
            title='Other Title',
            text='Other Text',
            slug='other-slug',
            author=cls.other_user,
        )
        cls.form_data = {
            'title': 'New Test Title',
            'text': 'New Test Text',
            'slug': 'new-test-slug',
        }
        cls.create_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.list_url = reverse('notes:list')

    def setUp(self):
        self.client.force_login(self.author)


class TestNoteLogic(BaseTestCase):
    """Тесты логики создания, редактирования и удаления заметок."""

    def test_anonymous_cant_create(self):
        """Аноним не может создать заметку."""
        self.client.logout()
        ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(self.create_url, data=self.form_data)
        expected_redirect = f'{self.login_url}?next={self.create_url}'
        self.assertRedirects(response, expected_redirect)
        ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(ids_before, ids_after)

    def test_user_can_create(self):
        """Авторизованный пользователь создает заметку."""
        ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(self.create_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        ids_after = set(Note.objects.values_list('id', flat=True))
        new_ids = ids_after - ids_before
        self.assertEqual(len(new_ids), 1)
        created_note = Note.objects.get(id=new_ids.pop())
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.slug, self.form_data['slug'])
        self.assertEqual(created_note.author, self.author)

    def test_slug_generated_if_missing(self):
        """Slug генерируется автоматически."""
        data_without_slug = {
            'title': 'Auto Slug Title',
            'text': 'Text for auto slug',
        }

        ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(self.create_url, data=data_without_slug)
        self.assertRedirects(response, self.success_url)
        ids_after = set(Note.objects.values_list('id', flat=True))
        new_ids = ids_after - ids_before
        self.assertEqual(len(new_ids), 1)
        created_note = Note.objects.get(id=new_ids.pop())
        self.assertTrue(created_note.slug)
        self.assertTrue(created_note.slug.isascii())
        self.assertNotIn(' ', created_note.slug)
        self.assertEqual(created_note.title, data_without_slug['title'])
        self.assertEqual(created_note.text, data_without_slug['text'])
        self.assertEqual(created_note.author, self.author)

    def test_unique_slug_validation(self):
        """Проверка уникальности slug: ошибка при дубликате."""
        duplicate_slug = 'duplicate-slug-test'
        Note.objects.create(
            title='Existing',
            text='Existing Text',
            slug=duplicate_slug,
            author=self.author,
        )
        data_with_duplicate = {
            'title': 'Another Title',
            'text': 'Another Text',
            'slug': duplicate_slug,
        }
        ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(self.create_url, data=data_with_duplicate)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('slug', response.context['form'].errors)
        ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(ids_before, ids_after)

    def test_author_can_delete(self):
        """Автор может удалить свою заметку."""
        ids_before = set(Note.objects.values_list('id', flat=True))
        self.assertIn(self.note.id, ids_before)
        response = self.client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertNotIn(self.note.id, ids_after)
        self.assertEqual(len(ids_before) - len(ids_after), 1)

    def test_user_cant_delete_another(self):
        """Пользователь не может удалить чужую заметку."""
        self.client.force_login(self.reader)
        ids_before = set(Note.objects.values_list('id', flat=True))
        note_fields_before = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.note.author,
        }
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(ids_before, ids_after)
        note_fresh = Note.objects.get(id=self.note.id)
        self.assertEqual(note_fresh.title, note_fields_before['title'])
        self.assertEqual(note_fresh.text, note_fields_before['text'])
        self.assertEqual(note_fresh.slug, note_fields_before['slug'])
        self.assertEqual(note_fresh.author, note_fields_before['author'])

    def test_author_can_edit(self):
        """Автор может редактировать свою заметку."""
        new_data = {
            'title': 'Edited Title',
            'text': 'Edited Text',
            'slug': 'edited-slug',
        }
        response = self.client.post(self.edit_url, data=new_data)
        self.assertRedirects(response, self.success_url)
        note_fresh = Note.objects.get(id=self.note.id)
        self.assertEqual(note_fresh.title, new_data['title'])
        self.assertEqual(note_fresh.text, new_data['text'])
        self.assertEqual(note_fresh.slug, new_data['slug'])
        self.assertEqual(note_fresh.author, self.author)

    def test_user_cant_edit_another(self):
        """Пользователь не может редактировать чужую заметку."""
        self.client.force_login(self.reader)
        new_data = {
            'title': 'Hacked Title',
            'text': 'Hacked Text',
            'slug': 'hacked-slug',
        }
        original_fields = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.note.author,
        }
        response = self.client.post(self.edit_url, data=new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_fresh = Note.objects.get(id=self.note.id)
        self.assertEqual(note_fresh.title, original_fields['title'])
        self.assertEqual(note_fresh.text, original_fields['text'])
        self.assertEqual(note_fresh.slug, original_fields['slug'])
        self.assertEqual(note_fresh.author, original_fields['author'])
