from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

LIMIT = 10


class TestNotesListContent(TestCase):
    """Проверка контента."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.other_user = User.objects.create(username='Other')
        cls.notes = []
        count = LIMIT + 1
        for i in range(count):
            note = Note.objects.create(
                title=f'Note {i}',
                text=f'Text {i}',
                slug=f'slug-{i}',
                author=cls.author,
            )
            cls.notes.append(note)
        cls.foreign_note = Note.objects.create(
            title='Foreign Note',
            text='Foreign Text',
            slug='foreign-slug',
            author=cls.other_user,
        )
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.notes[-1].slug,))

    def setUp(self):
        self.client.force_login(self.author)

    def test_note_in_context(self):
        """Заметка передается в object_list."""
        response = self.client.get(self.list_url)
        self.assertIn(self.notes[-1], response.context['object_list'])

    def test_no_foreign_notes(self):
        """Заметки другого пользователя не попадают в список."""
        response = self.client.get(self.list_url)
        self.assertNotIn(self.foreign_note, response.context['object_list'])

    def test_forms_in_context(self):
        """Формы передаются на страницы создания и редактирования."""
        urls = [self.add_url, self.edit_url]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
