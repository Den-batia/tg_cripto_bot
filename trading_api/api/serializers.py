from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from .models import User, Text


class WalletSerializer(ModelSerializer):
    class Meta:
        pass


class UserSerializer(ModelSerializer):
    invited_count = SerializerMethodField()

    class Meta:
        model = User
        fields = ('telegram_id', 'ref_code', 'invited_count')

    def get_invited_count(self, instance: User):
        return User.objects.filter(referred_from=instance).count()


class TextSerializer(ModelSerializer):
    class Meta:
        model = Text
        fields = ('text',)
