from notes.forms import NoteForm

from .base import LIST_URL, ADD_URL, EDIT_URL, BaseTestCase


class TestNotesListContent(BaseTestCase):
    """Проверка контента страниц списка заметок."""

    def test_note_in_context(self):
        """Заметка автора присутствует в списке, все поля корректны."""
        response = self.author_client.get(LIST_URL)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)
        context_note = notes.get(pk=self.note.pk)
        self.assertEqual(context_note.title, self.note.title)
        self.assertEqual(context_note.text, self.note.text)
        self.assertEqual(context_note.slug, self.note.slug)
        self.assertEqual(context_note.author, self.note.author)

    def test_no_foreign_notes(self):
        """Заметки других пользователей не попадают в список."""
        response = self.reader_client.get(LIST_URL)
        notes = response.context['object_list']
        self.assertEqual(len(notes), 0)

    def test_forms_in_context(self):
        """Формы передаются на страницы создания и редактирования."""
        urls = [ADD_URL, EDIT_URL]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)
