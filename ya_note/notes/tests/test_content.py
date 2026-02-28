from .base import BaseTestCase, LIST_URL


class TestNotesListContent(BaseTestCase):
    """Проверка контента страниц списка заметок."""

    def test_note_in_context(self):
        """Заметка автора присутствует в списке."""
        response = self.author_client.get(LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context)
        context_list = response.context['object_list']
        last_note = self.notes[-1]
        if hasattr(context_list, 'object_list'):
            objects = context_list.object_list
        else:
            objects = context_list
        self.assertIn(last_note, objects)

    def test_no_foreign_notes(self):
        """Заметки другого пользователя не попадают в список."""
        response = self.author_client.get(LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context)
        context_list = response.context['object_list']

        if hasattr(context_list, 'object_list'):
            objects = context_list.object_list
        else:
            objects = context_list
        self.assertNotIn(self.foreign_note, objects)

    def test_forms_in_context(self):
        """Формы передаются на страницы создания и редактирования."""
        urls = [self.add_url, self.edit_url]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertIsNotNone(response.context)
                self.assertIn('form', response.context)
