from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


def test_user_can_create_comment(
        author_client, author, form_data, pk_for_args, url_to_comment,
):
    url = reverse('news:detail', args=pk_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comment)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, pk_for_args):
    url = reverse('news:detail', args=pk_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client, form_data, comment, url_to_comment,
):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, url_to_comment)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_comment(author_client, comment, url_to_comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assertRedirects(response, url_to_comment)
    assert Comment.objects.count() == 0


def test_not_owner_cannot_delete_comment(admin_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_not_owner_cannot_edit_comment(admin_client, comment, form_data):
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get()
    assert new_comment.text != form_data['text']


def test_user_cannot_use_badwords_in_comment(
        author_client, bad_words_data, pk_for_args,
):
    url = reverse('news:detail', args=pk_for_args)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0
