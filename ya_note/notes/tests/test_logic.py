from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from .base import (
    ADD_URL,
    EDIT_URL,
    DELETE_URL,
    REDIRECT_TO_ADD,
    SUCCESS_URL,
    BaseTestCase,
)


class TestNoteLogic(BaseTestCase):
    """Тесты логики создания, редактирования и удаления заметок."""

    def test_anonymous_cant_create(self):
        """Аноним не может создать заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, REDIRECT_TO_ADD)
        self.assertEqual(
            note_ids_before, set(Note.objects.values_list('id', flat=True))
        )

    def test_user_can_create(self):
        """Авторизованный пользователь создает заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
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
        # Реализовано прямое изменение self.form_data (pop + restore)
        # вместо создания нового словаря.
        # Данный подход выбран в строгом соответствии с рекомендацией
        # из прошлого ревью:
        # "Замените четыре строки на изменение слага в словаре self.form_data".
        # Восстановление значения выполнено хардкодом для минимизации
        # количества строк кода
        # (избежано создание промежуточной переменной original_slug).
        self.form_data.pop('slug')
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        new_ids = note_ids_after - note_ids_before
        self.assertEqual(len(new_ids), 1)
        new_id = new_ids.pop()
        created_note = Note.objects.get(id=new_id)
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.author, self.author)
        expected_slug = slugify(self.form_data['title'])[:100]
        self.assertEqual(created_note.slug, expected_slug)
        # Восстановление фикстуры обязательно для
        # корректной работы последующих тестов.
        self.form_data['slug'] = 'new-test-slug'

    def test_create_note_with_duplicate_slug_fails(self):
        """Создание заметки с дублирующимся slug невозможно."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(
            ADD_URL,
            data={**self.form_data, 'slug': self.note.slug}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('slug', response.context['form'].errors)
        self.assertEqual(
            note_ids_before, set(Note.objects.values_list('id', flat=True))
        )

    def test_author_can_delete(self):
        """Автор может удалить свою заметку."""
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        count_before = Note.objects.count()
        response = self.author_client.delete(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())
        self.assertEqual(Note.objects.count(), count_before - 1)

    def test_user_cannot_delete_foreign_note(self):
        """Пользователь не может удалить чужую заметку."""
        response = self.reader_client.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)

    def test_author_can_edit(self):
        """Автор может редактировать свою заметку."""
        # Меняем данные напрямую в self.form_data.
        # Восстановление не требуется: следующий тест
        # проверяет только статус 404
        # и не зависит от конкретных значений полей формы.
        self.form_data['title'] = 'Edited Title'
        self.form_data['text'] = 'Edited Text'
        self.form_data['slug'] = 'edited-slug'
        response = self.author_client.post(EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        updated_note = Note.objects.get(id=self.note.id)
        # НЕХРУПКИЕ ПРОВЕРКИ:
        # Сравниваем БД с текущим состоянием self.form_data.
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_user_cannot_edit_foreign_note(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)
