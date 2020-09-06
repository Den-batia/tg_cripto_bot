from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from api.api import UserInfoViewSet
from api.models import User
from api.tests.abstract_test import AbstractAPITestCase


class UserInfoTest(AbstractAPITestCase):
    def _get_uri(self, *args):
        return reverse('user-info-detail', args)

    def setUp(self) -> None:
        super().setUp()
        self.view = UserInfoViewSet.as_view({'get': 'retrieve'})

    def test_list(self):
        user = User.objects.create(telegram_id=23456)
        response = self._make_get_request(view=self.view, uri=self._get_uri(user.nickname,), nickname=user.nickname)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['nickname'], user.nickname)
