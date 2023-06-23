from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class Tests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Pushkin')
        cls.reader = User.objects.create(username='Lermontov')
        cls.note = Note.objects.create(
            title='Новая запись',
            text='Запись для теста',
            author=cls.author,
        )

    def test_homepage(self):
        """
        Страницы домашняя, логин, логаут, регистрация
        доступны для всех.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_pages_list_add_done(self):
        """
        Страницы добавление записи, список записей,
        успешного добавления/редактирования/удаления записи
        доступны авторизованному пользователю.
        """
        user = self.author
        self.client.force_login(user)
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_delete_detail(self):
        """
        Пользователь может редактировать и удалять свои записи
        и не может редактировать и удалять чужие записи.
        """
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Неавторизованный пользователь при поптыке посетить страницы
        редактирования записи, удаления записи, детали записи,
        добавление записи, список записей, успешного
        добавления/редактирования/удаления записи
        будет переадресован на страницу авторизации.
        """
        login_url = reverse('users:login')
        for name, args in (
                ('notes:edit', (self.note.slug,)),
                ('notes:delete', (self.note.slug,)),
                ('notes:detail', (self.note.slug,)),
                ('notes:add', None),
                ('notes:list', None),
                ('notes:success', None),
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
