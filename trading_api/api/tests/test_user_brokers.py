from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from api.api import UserBrokerView
from api.models import User, Broker, Requisite
from api.tests.abstract_test import AbstractAPITestCase

class UserBrokersTest(AbstractAPITestCase):

    def _get_uri(self, *args, **kwargs):
        return reverse('user-brokers', args, kwargs)

    def setUp(self) -> None:
        super().setUp()
        self.view = UserBrokerView.as_view()


    def test_get(self):
        user = User.objects.create(telegram_id=23456)
        broker = Broker.objects.create(name='Банковский перевод внутри страны')
        requisite = Requisite.objects.create(user=user, broker=broker, requisite='бабло сюда кидай!!!')

        response = self._make_get_request(view=self.view, uri=self._get_uri(user_id=user.id, broker_id=broker.id), user_id=user.id, broker_id=broker.id)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['requisite'], requisite.requisite)

    def test_get_404(self):
        user = User.objects.create(telegram_id=23456)
        user_1 = User.objects.create(telegram_id=2346)
        broker = Broker.objects.create(name='Банковский перевод внутри страны')
        requisite = Requisite.objects.create(user=user, broker=broker, requisite='бабло сюда кидай!!!')

        response = self._make_get_request(view=self.view, uri=self._get_uri(user_id=user_1.id, broker_id=broker.id), user_id=user_1.id, broker_id=broker.id)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_path(self):
        user = User.objects.create(telegram_id=23456)
        broker = Broker.objects.create(name='Банковский перевод внутри страны')
        requisite = Requisite.objects.create(user=user, broker=broker, requisite='бабло сюда кидай!!!')
        data = {
            'requisite': 'Нет, лучше люда =>'
        }
        response = self._make_patch_request(data, uri=self._get_uri(user_id=user.id, broker_id=broker.id), user_id=user.id, broker_id=broker.id)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['requisite'], data['requisite'])
