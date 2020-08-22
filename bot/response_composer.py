from .keyboards import kb
from .translations.translations import translate

verify_sm = {True: '✅', False: '❌'}


lang = 'ru'


class ResponseComposer:
    # async def _get(self, *, var_name, **kwargs):
    #     kwargs['support'] = SUPPORT
    #     text: str = await api.get_text(var_name)
    #     return text.format(**kwargs).expandtabs(2)

    async def _get(self, *, var_name, **kwargs):
        return translate(f'misc.{var_name}', locale=lang, **kwargs).expandtabs(2)

    async def _big_number_str(self, value):
        return "{:,}".format(value)

    async def start(self):
        text = await self._get(var_name='start')
        k = await kb.main_menu()
        return text, k

    async def done(self):
        text = await self._get(var_name="done")
        k = await kb.main_menu()
        return text, k

    async def get_main_k(self):
        return await kb.main_menu()

    async def unknown_error(self):
        text = await self._get(var_name='unknown_error')
        k = await kb.main_menu()
        return text, k

    async def unknown_command(self):
        text = await self._get(var_name='unknown_command')
        k = await kb.main_menu()
        return text, k

    async def about(self):
        text = await self._get(var_name='about')
        k = await kb.ref()
        return text, k

    async def referral(self):
        text = await self._get(var_name='referral')
        k = await kb.main_menu()
        return text, k

    async def accounts(self, symbols):
        text = await self._get(var_name='accounts')
        k = await kb.accounts(symbols)
        return text, k

    async def account_not_exists(self, symbol_id):
        text = await self._get(var_name='account_not_exists')
        k = await kb.create_account(symbol_id)
        return text, k

    async def account(self, account, user):
        text = await self._get(var_name='account', balance=float(account['balance']),
                               symbol=account['symbol']['name'].upper(), frozen=account['frozen'],
                               nickname=user['nickname'])
        k = await kb.account(account)
        return text, k

    async def market_choose_symbol(self, symbols):
        text = await self._get(var_name='market_choose_symbol')
        k = await kb.market_choose_symbol(symbols)
        return text, k

    async def symbol_market(self, symbol):
        text = await self._get(var_name='symbol_market')
        k = await kb.symbol_market(symbol)
        return text, k

    async def symbol_market_action(self, symbol, orders, action):
        text = await self._get(var_name=action, symbol=symbol['name'].upper())
        k = await kb.symbol_market_action(symbol, orders, action)
        return text, k

    async def symbol_broker_market(self, symbol, broker, orders, action):
        text = await self._get(var_name=f'broker_{action}', symbol=symbol['name'].upper(), broker=broker['name'])
        k = await kb.symbol_broker_market(symbol, orders, action=action)
        return text, k

    async def get_update_deposit(self, amount, symbol, **kwargs):
        text = await self._get(var_name='deposit_notification', symbol=symbol.upper(), amount=amount)
        k = None
        return text, k

    async def get_update_withdraw(self, link, **kwargs):
        text = await self._get(var_name='withdraw_notification', link=link)
        k = None
        return text, k

    async def get_update_new_deal(self, **kwargs):
        deal = kwargs['data']
        action = await self._get(var_name=f'new_deal_notification_{deal["order"]["type"]}')
        nickname = deal[('seller' if deal['order']['type'] == 'buy' else 'buyer')]['nickname']
        symbol = deal.pop('symbol')['name'].upper()
        text = await self._get(var_name='new_deal_notification', action=action, nickname=nickname, symbol=symbol, **deal)
        k = await kb.confirm_deal(deal['id'])
        return text, k

    async def get_update_deal_accepted(self, **kwargs):
        deal = kwargs['data']
        text = await self._get(var_name='deal_accepted_notification', broker=deal['order']['broker']['name'], **deal)
        k = None
        return text, k

    async def get_update_deal_declined(self, **kwargs):
        deal = kwargs['data']
        text = await self._get(var_name='deal_declined_notification', **deal)
        k = None
        return text, k

    async def get_update_requisite_only(self, **kwargs):
        deal = kwargs['data']
        text = f"<pre>{deal['requisite']}</pre>"
        k = await kb.send_fiat(deal['id'])
        return text, k

    async def get_update_fiat_sent(self, **kwargs):
        deal = kwargs['data']
        text = await self._get(var_name='deal_fiat_sent_notification', broker=deal['order']['broker']['name'], **deal)
        k = await kb.send_crypto(deal['id'])
        return text, k

    async def get_update_crypto_sent(self, **kwargs):
        deal = kwargs['data']
        text = await self._get(var_name='deal_crypto_sent_notification', symbol=deal.pop('symbol')['name'].upper(), **deal)
        k = None
        return text, k

    async def get_update_crypto_received(self, **kwargs):
        deal = kwargs['data']
        text = await self._get(var_name='deal_crypto_received_notification', symbol=deal.pop('symbol')['name'].upper(), **deal)
        k = None
        return text, k

    async def get_update_deal_timeout(self, **kwargs):
        text = await self._get(var_name='deal_timeout_notification', **kwargs)
        k = None
        return text, k

    async def get_update_message_received(self, **kwargs):
        text = await self._get(var_name='message_received', text=kwargs['text'], nickname=kwargs['user']['nickname'])
        k = await kb.send_message(kwargs['user'])
        return text, k

    async def cancel(self):
        text = await self._get(var_name='cancel')
        k = await kb.main_menu()
        return text, k

    async def not_enough_money_withdraw(self):
        text = await self._get(var_name='not_enough_money')
        k = await kb.main_menu()
        return text, k

    async def address_validation_failed(self):
        text = await self._get(var_name='address_validation_failed')
        k = await kb.main_menu()
        return text, k

    async def enter_address(self):
        text = await self._get(var_name='enter_address')
        k = await kb.get_cancel()
        return text, k

    async def enter_amount_withdraw(self, balance, min_withdraw, symbol):
        text = await self._get(var_name='enter_amount_withdraw', balance=balance, min_withdraw=min_withdraw, symbol=symbol)
        k = await kb.get_cancel()
        return text, k

    async def transaction_queued(self):
        text = await self._get(var_name='transaction_queued')
        k = await kb.main_menu()
        return text, k

    async def wrong_amount(self):
        text = await self._get(var_name='wrong_amount')
        k = await kb.main_menu()
        return text, k

    async def my_orders(self, orders, symbol_id):
        text = await self._get(var_name='my_orders')
        k = await kb.my_orders(orders, symbol_id)
        return text, k

    async def order(self, order, is_my):
        text = await self._get(var_name=order['type'], symbol=order['symbol']['name'].upper(), id=order['id'])
        text += '\n\n'
        user = order.pop('user')
        text += await self._get(
            var_name='user',
            verify=verify_sm[user.pop('is_verify')],
            **user
        )
        text += '\n\n'
        text += await self._get(var_name='order', active=verify_sm[order['is_active']], broker=order.pop('broker')['name'], **order)
        if order['details']:
            text += '\n'
            text += await self._get(var_name='order_details', details=order['details'])
        if is_my:
            k = await kb.my_order(order)
        else:
            k = await kb.market_order(order['id'])
        return text, k

    async def user(self, user, is_admin):
        text = await self._get(var_name='user', verify=verify_sm[user['is_verify']], **user)
        if is_admin:
            k = await kb.user_admin_actions(user)
        else:
            k = await kb.send_message(user)
        return text, k

    async def send_message(self):
        text = await self._get(var_name='send_message')
        k = await kb.get_cancel()
        return text, k

    async def message_sent(self):
        text = await self._get(var_name='message_sent')
        k = await kb.main_menu()
        return text, k

    async def new_order(self, symbol_id):
        text = await self._get(var_name='new_order')
        k = await kb.new_order_create(symbol_id)
        return text, k

    async def new_order_brokers(self, brokers):
        text = await self._get(var_name='new_order_brokers')
        k = await kb.get_new_brokers(brokers, [])
        return text, k

    async def get_new_order_brokers_kb(self, brokers, chosen_brokers):
        k = await kb.get_new_brokers(brokers, chosen_brokers)
        return k

    async def choose_limits(self):
        text = await self._get(var_name='choose_limits')
        k = await kb.get_cancel()
        return text, k

    async def choose_rate(self):
        text = await self._get(var_name='choose_rate')
        k = await kb.get_cancel()
        return text, k

    async def choose_details(self):
        text = await self._get(var_name='choose_details')
        k = await kb.get_cancel()
        return text, k

    async def delete_order_confirmation(self):
        text = await self._get(var_name='delete_order_confirmation')
        k = await kb.are_you_sure()
        return text, k

    async def requisites(self, brokers):
        text = await self._get(var_name='requisites_settings')
        k = await kb.requisites(brokers)
        return text, k

    async def broker_requisite(self, requisite, broker):
        text = await self._get(var_name='requisite_settings', requisite=requisite, broker_name=broker['name'])
        k = await kb.broker_requisite(broker)
        return text, k

    async def edit_broker_requisite(self, broker):
        text = await self._get(var_name='edit_broker_requisite', broker_name=broker['name'])
        k = await kb.get_cancel()
        return text, k

    async def enter_amount_begin_deal(self, min_amount, max_amount):
        text = await self._get(var_name='enter_amount_begin_deal', min=min_amount, max=max_amount)
        k = await kb.get_cancel()
        return text, k

    async def begin_deal_confirmation(self, order, amount, amount_crypto, requisite, reversed_actions):
        action = await self._get(var_name=f'action_{reversed_actions[order["type"]]}')
        text = await self._get(var_name='begin_deal_confirmation', amount=amount, amount_crypto=amount_crypto,
                               action=action, symbol=order.pop('symbol')['name'].upper(),
                               broker=order.pop('broker')['name'], **order)
        if requisite is not None:
            text += '\n\n'
            text += await self._get(var_name='deal_requisite', requisite=requisite)
        k = await kb.are_you_sure()
        return text, k

    async def deal(self, deal, user=None):
        text = await self._get(var_name='deal', buyer=deal['buyer']['nickname'], seller=deal['seller']['nickname'],
                               symbol=deal['symbol']['name'].upper(), amount_currency=deal['amount_currency'],
                               amount_crypto=deal['amount_crypto'], broker=deal['order']['broker']['name'],
                               requisite=deal['requisite'], id=deal['id'], rate=deal['rate'])
        k = await kb.main_menu()
        if user:
            if user['id'] == deal['buyer']['id'] and deal['status'] == 1:
                k = await kb.send_fiat(deal['id'])
            elif user['id'] == deal['seller']['id'] and deal['status'] == 2:
                k = await kb.send_crypto(deal['id'])
            elif deal['status'] == 0 and user['id'] == deal['order']['user']['id']:
                k = await kb.confirm_deal(deal['id'])
        return text, k

    async def balance(self, balance):
        text = ''
        for b in balance:
            text += '\n\n'
            text += await self._get(
                var_name='balance', wallet=b['wallet'],
                db=b['db'], symbol=b['symbol'].upper(),
                balance=b['balance']
            )
        k = await kb.main_menu()
        return text, k


rc = ResponseComposer()
