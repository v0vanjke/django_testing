from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Pushkin')
        cls.reader = User.objects.create(username='Lermontov')
        cls.note = Note.objects.create(
            title='Новая запись',
            text='Запись для теста',
            author=cls.author,
        )

    def test_notes_lists_are_different_for_different_users(self):
        """
        На странице списка записей авторизованного пользователя
        отображаются только его записи.
        """
        user_noteincludedstatus = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')
        for user, notestatus in user_noteincludedstatus:
            self.client.force_login(user)
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertEqual(self.note in object_list, notestatus)

    def test_authorized_client_has_form(self):
        """
        На страницах добавления и редактирования записи
        у аторизованного пользователя есть форма.
        """
        for name, slug in (
                ('notes:add', None),
                ('notes:edit', (self.note.slug,))
        ):
            with self.subTest(name=name):
                url = reverse(name, args=slug)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
