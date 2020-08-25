from django.urls import path
from rest_framework import routers

from .api import (
    NewUserView, UserViewSet, TextViewSet,
    UserAccountsViewSet, SymbolsViewSet,
    GenerateAccountView, AggregatedOrderView, OrderViewSet, BrokersViewSet, NewOrderView, AddressCheckView,
    NewWithdrawView, UserOrdersViewSet, TgUserViewSet, UserInfoViewSet, OrderInfoViewSet, UserBrokerView, NewDealView,
    DealDetailViewSet, ConfirmDealView, DeclineDealView, SendFiatDealView, SendCryptoDealView, NewMessageView,
    BalanceView, RateUserView, NicknameChangeView
)

router = routers.DefaultRouter()

router.register('v1/tg-users', TgUserViewSet, 'tg-users')
router.register('v1/users', UserViewSet, 'users')
router.register('v1/texts', TextViewSet, 'texts')
router.register('v1/symbols', SymbolsViewSet, 'symbol')
router.register('v1/brokers', BrokersViewSet, 'brokers')
router.register('v1/accounts', UserAccountsViewSet, 'accounts')
router.register('v1/orders', OrderViewSet, 'orders')
router.register('v1/deals', DealDetailViewSet, 'deals')
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
    path('v1/aggregated-orders/', AggregatedOrderView.as_view(), name='aggregated-orders'),
    path('v1/users/<uuid:user_id>/brokers/<int:broker_id>/', UserBrokerView.as_view(), name='user-brokers'),
    path('v1/messages/new', NewMessageView.as_view(), name='new-message'),
    path('v1/deals/new', NewDealView.as_view(), name='new-deal'),
    path('v1/deals/<str:deal_id>/confirm/', ConfirmDealView.as_view(), name='confirm-deal'),
    path('v1/deals/<str:deal_id>/decline/', DeclineDealView.as_view(), name='decline-deal'),
    path('v1/deals/<str:deal_id>/send_fiat/', SendFiatDealView.as_view(), name='send-fiat-deal'),
    path('v1/deals/<str:deal_id>/send_crypto/', SendCryptoDealView.as_view(), name='send-crypto-deal'),
    path('v1/deals/<str:deal_id>/rate/', RateUserView.as_view(), name='rate-user-deal'),
    path('v1/users/<str:user_id>/nickname/', NicknameChangeView.as_view(), name='nickname-change'),
    path('v1/balance', BalanceView.as_view(), name='balance'),
]
