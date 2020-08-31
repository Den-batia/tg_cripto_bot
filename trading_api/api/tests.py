from rest_framework.test import APITestCase
from django.urls import reverse, path, include
from rest_framework.generics import get_object_or_404
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from rest_framework import status
from .api import TgUserViewSet
from .models import User, Symbol, Account
from .urls import urlpatterns


class UsersTest(APITestCase):

    # def setUp(self):
        # User.objects.create(telegram_id=1234567)
        #
        # User.objects.create(telegram_id=9876543,
        #                     nickname='DenBatia',
        #                     is_admin=True,
        #                     is_verify=True)
        #
        # User.objects.create(telegram_id=5681111,
        #                     nickname='Den',
        #                     is_admin=False,
        #                     is_verify=False)

    def test_users(self):
        url = reverse('users-list')
        response = self.client.post(url, {'telegram_id': '5478300111'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['telegram_id'], 5478300111)
        self.assertEqual(len(User.objects.all()), 1)

        url = reverse('users-detail', args=(response.data['nickname'],))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(User.objects.all()), 0)

    def test_tg_users(self):
        url = reverse('users-list')
        response = self.client.post(url, {'telegram_id': '5478300111'})
        response = self.client.delete(reverse('tg-users-detail', args=(response.data['nickname'],)))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_symbol(self):
        lst = [Symbol(name='etc'), Symbol(name='usdt')]
        Symbol.objects.bulk_create(lst)
        url = reverse('symbol-list')
        response = self.client.get(url)
        """????????"""
        self.assertEqual(len(response.data), 3)
        """????????"""
        response = self.client.delete(reverse('symbol-detail', args=('etc',)))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_generate_accounts__accounts(self):
        user = User(telegram_id=555444222)
        user_2 = User(telegram_id=3456112)
        user.save()
        user_2.save()

        symbol = get_object_or_404(Symbol, name='eth')

        url = reverse('generate-account')
        response = self.client.post(url, {'user_id': user.id, 'symbol': symbol.id})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('accounts-detail', args=(user.id,))
        response = self.client.get(url)
        url_2 = reverse('accounts-detail', args=(user_2.id,))
        response_2 = self.client.get(url_2)
        self.assertGreaterEqual(len(response.data['accounts']), 0)
        self.assertEqual(len(response_2.data['accounts']), 0)




