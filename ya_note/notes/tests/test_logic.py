# news/tests/test_logic.py
from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Pushkin')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': 'Random title',
            'text': 'Note text',
            'slug': 'New-slug',
        }

    def test_anonymous_user_cant_create_note(self):
        """
        Неавторизованный пользователь неможет оставить запись.
        """
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """
        Авторизованный пользователь может оставить запись.
        """
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_empty_slug(self):
        """
        При добавлении записи с пустым заголовком,
        заголовок заполняется автоматически.
        """
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteCreationIfSlugIsAlreadyExists(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Pushkin')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': 'Random title',
            'text': 'Note text',
            'slug': 'New-slug',
        }
        cls.note = Note.objects.create(
            title='Новая запись',
            text='Запись для теста',
            author=cls.user,
        )

    def test_not_unique_slug(self):
        """
        При добавлении записей с одинаковым загооловком,
        запись не создается, а пользователь получает предупреждение.
        """
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING),
        )
        self.assertEqual(Note.objects.count(), 1)


class TestCommentEditDelete(TestCase):
    NOTE_TEXT = 'Текст'
    NOTE_UPDATED_TEXT = 'Updated note.text'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Pushkin')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Lermontov')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.note.title,
            'text': cls.NOTE_UPDATED_TEXT,
            'author': cls.author,
        }

    def test_author_can_delete_note(self):
        """
        Автор записи может ее удалить.
        """
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """
        Авторизованный пользователь не может удалить чужую запись.
        """
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """
        Автор может редактировать свои записи.
        """
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_UPDATED_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """
        Авторизованный пользователь не может редактировать не сови записи.
        """
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
