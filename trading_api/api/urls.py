from django.urls import path
from rest_framework import routers

from .api import (
    NewUserView, UserViewSet, TextViewSet,
    UserAccountsViewSet, SymbolsViewSet,
    GenerateAccountView, AggregatedOrderView
)

router = routers.DefaultRouter()

router.register('v1/tg-users', UserViewSet, 'tg-users')
router.register('v1/texts', TextViewSet, 'texts')
router.register('v1/symbols', SymbolsViewSet, 'symbol')
router.register('v1/accounts', UserAccountsViewSet, 'accounts')

urlpatterns = router.urls


urlpatterns += [
    path('v1/tg-users/new', NewUserView.as_view(), name='new-tg-user'),
    path('v1/accounts/generate', GenerateAccountView.as_view(), name='generate-account'),
    path('v1/aggregated-orders', AggregatedOrderView.as_view(), 'aggregated-orders')

]
