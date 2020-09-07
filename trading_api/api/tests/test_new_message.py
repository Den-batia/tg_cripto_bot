from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from api.api import NewMessageView
from api.models import User
from api.tests.abstract_test import AbstractAPITestCase
from unittest.mock import patch

class NewMessageTest(AbstractAPITestCase):

    def _get_uri(self, *args, **kwargs):
        return reverse('send-fiat-deal', args, kwargs)

    def setUp(self) -> None:
        super().setUp()
        self.view = NewMessageView.as_view()

    @patch('utils.redis_queue.NotificationsQueue.put')
    def test_(self, put):
        buyer = User.objects.create(telegram_id=2345)
        user = User.objects.create(telegram_id=23456)
        data = {
            'sender_id': user.id,
            'receiver_id': buyer.id,
            'text': 'Ну дароу!!!'
        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    @patch('utils.redis_queue.NotificationsQueue.put')
    def test_invalid_user(self, put):
        buyer = User.objects.create(telegram_id=2345)
        user = User.objects.create(telegram_id=23456)
        data = {
            'sender_id': '18798987678',
            'receiver_id': buyer.id,
            'text': 'Ну дароу!!!'
        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)