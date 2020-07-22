from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import User, Text
from .serializers import UserSerializer, TextSerializer


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
            user = User.objects.create(telegram_id=telegram_id)
            if referred_from:
                user.referred_from = referred_from
            user.save()
        return Response(UserSerializer(user).data, status=HTTP_201_CREATED)


class TextViewSet(ReadOnlyModelViewSet):
    serializer_class = TextSerializer
    queryset = Text.objects.all()
    lookup_field = 'name'
