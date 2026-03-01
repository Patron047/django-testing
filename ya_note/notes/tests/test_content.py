from notes.forms import NoteForm

from .base import LIST_URL, BaseTestCase


class TestNotesListContent(BaseTestCase):
    """Проверка контента страниц списка заметок."""

    def test_note_in_context(self):
        """Заметка автора присутствует в списке, все поля корректны."""
        response = self.author_client.get(LIST_URL)
        notes = response.context['object_list']
        context_note = None
        for note in notes:
            if note.slug == self.note.slug:
                context_note = note
                break
        self.assertIsNotNone(context_note, "Заметка не найдена в контексте")
        self.assertEqual(context_note.title, self.note.title)
        self.assertEqual(context_note.text, self.note.text)
        self.assertEqual(context_note.slug, self.note.slug)
        self.assertEqual(context_note.author, self.note.author)

    def test_no_foreign_notes(self):
        """Заметки другого пользователя не попадают в список."""
        response = self.author_client.get(LIST_URL)
        notes = response.context['object_list']
        self.assertNotIn(self.another_note, notes)

    def test_forms_in_context(self):
        """Формы передаются на страницы создания и редактирования."""
        urls = [self.add_url, self.edit_url]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)
