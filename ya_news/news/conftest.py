# conftest.py
import pytest
from django.urls import reverse
from news.models import News, Comment
from news.forms import BAD_WORDS

from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone


def pytest_configure():
    pytest.HOME_URL = reverse('news:home')


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Random text',
    )
    return comment


@pytest.fixture
def pk_for_args(news):
    return news.pk,


@pytest.fixture
def url_to_comment(news):
    new_url = reverse('news:detail', args=(news.id,))
    url_to_comment = new_url + '#comments'
    return url_to_comment


@pytest.fixture
def form_data(author):
    return {
        'text': 'Новый текст',
        'author': author,
    }


@pytest.fixture
def bad_words_data(author):
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture
def news_list():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment_list(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
