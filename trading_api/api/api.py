from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import User, Address
from .serializers import UserSerializer
from crypto.btc import BTC


class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'telegram_id'


class NewUserView(APIView):
    def post(self, request, *args, **kwargs):
        telegram_id = request.data['telegram_id']
        ref_code = request.data.get('ref')
        user = User.objects.filter(telegram_id=telegram_id).first()
        if user is None:
            referred_from = User.objects.filter(ref_code=ref_code).first() if ref_code else None
            user = User.objects.create(telegram_id=telegram_id, address=BTC.get_new_address())
            if referred_from:
                user.referred_from = referred_from
            user.save()
        return Response(UserSerializer(user).data, status=HTTP_201_CREATED)


class AddressCheck(APIView):
    def post(self, request, *args, **kwargs):
        address = request.data['address']
        telegram_id = request.data['telegram_id']
        user = User.objects.get(telegram_id=telegram_id)

        if user.balance_requests < 1:
            raise ValidationError

        address_object = Address.objects.filter(address=address).first()

        user.balance_requests -= 1
        user.save()

        if address_object is None:
            return Response(data={'status': 0})
