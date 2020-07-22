from django.urls import path
from rest_framework import routers

from .api import NewUserView, UserViewSet

router = routers.DefaultRouter()

router.register('v1/tg-users', UserViewSet, 'tg-users')

urlpatterns = router.urls


urlpatterns += [
    path('v1/tg-users/new', NewUserView.as_view(), name='new-tg-user'),
]
