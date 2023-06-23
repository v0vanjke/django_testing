# test_content.py
import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
        ('news:edit', pytest.lazy_fixture('pk_for_args'))
    )
)
def test_pages_contains_form_for_auth_user(
        author_client, name, args, news, comment,
):
    """
    Проверяем наличие формы комментария
    для авторизованного пользователя.
    """
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
        ('news:edit', pytest.lazy_fixture('pk_for_args'))
    )
)
def test_anonymous_client_has_no_form(client, news, comment, name, args):
    """
    Проверяем отсутсвие формы комментария
    для неавторизованного пользователя.
    """
    response = client.get(name, args=args)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_news_count(client, news_list):
    """
    Количество новостей на главной странице = 10.
    """
    response = client.get(pytest.HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list):
    """
    Новости на главной странице
    должны размещаться от новых к старым.
    """
    response = client.get(pytest.HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(news, client, comment_list):
    """
    Комментарии на странице новости
    должны отображаться от старых к новым.
    """
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created
