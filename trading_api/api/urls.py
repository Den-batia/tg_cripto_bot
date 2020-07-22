from django.urls import path
from rest_framework import routers

from .api import NewUserView, UserViewSet, AddressCheck

router = routers.DefaultRouter()

router.register('v1/tg-users', UserViewSet, 'tg-users')
router.register('v1/texts', TextViewSet, 'texts')

urlpatterns = router.urls


urlpatterns += [
    path('v1/tg-users/new', NewUserView.as_view(), name='new-tg-user'),
]
