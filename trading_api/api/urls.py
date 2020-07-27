from django.urls import path
from rest_framework import routers

from .api import (
    NewUserView, UserViewSet, TextViewSet,
    UserAccountsViewSet, SymbolsViewSet,
    GenerateAccountView, AggregatedOrderView, OrderViewSet, BrokersViewSet, NewOrderView
)

router = routers.DefaultRouter()

router.register('v1/tg-users', UserViewSet, 'tg-users')
router.register('v1/texts', TextViewSet, 'texts')
router.register('v1/symbols', SymbolsViewSet, 'symbol')
router.register('v1/brokers', BrokersViewSet, 'brokers')
router.register('v1/accounts', UserAccountsViewSet, 'accounts')
router.register('v1/orders', OrderViewSet, 'orders')

urlpatterns = router.urls


urlpatterns += [
    path('v1/tg-users/new', NewUserView.as_view(), name='new-tg-user'),
    path('v1/orders/new', NewOrderView.as_view(), name='new-order'),
    path('v1/accounts/generate', GenerateAccountView.as_view(), name='generate-account'),
    path('v1/aggregated-orders/', AggregatedOrderView.as_view(), name='aggregated-orders')
]
