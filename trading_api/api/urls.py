from django.urls import path
from rest_framework import routers

from .api import (
    NewUserView, UserViewSet, TextViewSet,
    UserAccountsViewSet, SymbolsViewSet,
    GenerateAccountView, AggregatedOrderView, OrderViewSet, BrokersViewSet, NewOrderView, AddressCheckView,
    NewWithdrawView, UserOrdersViewSet, TgUserViewSet, UserInfoViewSet, OrderInfoViewSet
)

router = routers.DefaultRouter()

router.register('v1/tg-users', TgUserViewSet, 'tg-users')
router.register('v1/users', UserViewSet, 'users')
router.register('v1/texts', TextViewSet, 'texts')
router.register('v1/symbols', SymbolsViewSet, 'symbol')
router.register('v1/brokers', BrokersViewSet, 'brokers')
router.register('v1/accounts', UserAccountsViewSet, 'accounts')
router.register('v1/orders', OrderViewSet, 'orders')
router.register('v1/users/(?P<user_id>[0-9a-f-]+)/orders', UserOrdersViewSet, 'user-orders')
router.register('v1/user-info', UserInfoViewSet, 'user-info')
router.register('v1/order-info', OrderInfoViewSet, 'order-info')

urlpatterns = router.urls

urlpatterns += [
    path('v1/tg-users/new', NewUserView.as_view(), name='new-tg-user'),
    path('v1/orders/new', NewOrderView.as_view(), name='new-order'),
    path('v1/accounts/generate', GenerateAccountView.as_view(), name='generate-account'),
    path('v1/address-check', AddressCheckView.as_view(), name='address-check'),
    path('v1/withdraws/new', NewWithdrawView.as_view(), name='new-withdraw'),
    path('v1/aggregated-orders/', AggregatedOrderView.as_view(), name='aggregated-orders')
]
