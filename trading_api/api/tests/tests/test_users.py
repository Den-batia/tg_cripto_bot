from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_405_METHOD_NOT_ALLOWED, HTTP_204_NO_CONTENT

from api.api import UserViewSet
from api.models import User
from api.tests.abstract_test import AbstractAPITestCase


class UserModelTest(AbstractAPITestCase):
    def _get_uri(self, *args):
        return reverse('users-detail', args)

    def setUp(self) -> None:
        super().setUp()
        self.view = UserViewSet.as_view({
            'post': 'create',
            'get': 'list',
            'delete': 'destroy',
            'patch': 'partial_update'
        })
        self.uri = reverse('users-list')

    def test_create(self):
        data = {"telegram_id": 1234}
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        user = User.objects.filter(telegram_id=1234).get()
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['nickname'], user.nickname)

    def test_list(self):
        lst = [User(telegram_id=23456), User(telegram_id=65783)]
        User.objects.bulk_create(lst)
        response = self._make_get_request(view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), User.objects.count())

    def test_destroy(self):
        user = User(telegram_id=23456)
        user.save()
        response = self._make_delete_request(view=self.view, uri=self._get_uri(user.nickname,), nickname=user.nickname)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)

    def test_detail(self):
        user = User(telegram_id=23456)
        user.save()
        response = self._make_get_request(view=self.view, uri=self._get_uri(user.nickname,))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data[0]['nickname'], user.nickname)

    def test_patch(self):
        user = User(telegram_id=23456)
        user.save()
        data = {
            'nickname': 'data333j',
            'is_admin': True
        }
        response = self._make_patch_request(data, view=self.view, uri=self._get_uri(user.nickname, ), nickname=user.nickname)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['is_admin'], data['is_admin'])
        self.assertEqual(response.data['nickname'], data['nickname'])