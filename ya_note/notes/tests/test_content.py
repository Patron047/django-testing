from django.conf import settings
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс для общих тестовых данных и URL."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.other_user = User.objects.create(username='Other')
        count = settings.LIMIT_NOTES_ON_PAGE + 1
        cls.notes = []
        for i in range(count):
            note = Note.objects.create(
                title=f'Note {i}',
                text=f'Text {i}',
                slug=f'slug-{i}',
                author=cls.author,
            )
            cls.notes.append(note)
        cls.other_note = Note.objects.create(
            title='Other Note',
            text='Other Text',
            slug='other-slug',
            author=cls.other_user,
        )
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        last_slug = cls.notes[-1].slug
        cls.edit_url = reverse('notes:edit', args=(last_slug,))
        cls.delete_url = reverse('notes:delete', args=(last_slug,))
        cls.detail_url = reverse('notes:detail', args=(last_slug,))

    def setUp(self):
        self.client.force_login(self.author)


class TestNotesListContent(BaseTestCase):
    """Проверка контента страниц списка заметок."""

    def test_note_in_context(self):
        """Заметка передается в object_list с корректными полями."""
        response = self.client.get(self.list_url)
        context_list = response.context['object_list']
        last_note = self.notes[-1]
        self.assertIn(last_note, context_list)
        context_note = None
        for note in context_list:
            if note.id == last_note.id:
                context_note = note
                break
        self.assertIsNotNone(context_note)
        self.assertEqual(context_note.title, last_note.title)
        self.assertEqual(context_note.text, last_note.text)
        self.assertEqual(context_note.slug, last_note.slug)
        self.assertEqual(context_note.author, last_note.author)

    def test_no_other_notes_in_list(self):
        """Заметки другого пользователя не попадают в список."""
        response = self.client.get(self.list_url)
        self.assertNotIn(self.other_note, response.context['object_list'])

    def test_forms_in_context(self):
        """Формы правильного типа передаются на страницы."""
        urls = [self.add_url, self.edit_url]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'],
                    ModelForm,
                    'Форма должна быть экземпляром ModelForm',
                )
