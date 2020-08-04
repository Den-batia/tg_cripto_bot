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

    async def friends(self, user, friends_cnt):
        text = await self._get(var_name='friends_message', friends_cnt=friends_cnt)
        k = await kb.main_menu(user['city'])
        return text, k

    async def help(self, user):
        text = await self._get(var_name="help_message")
        k = await kb.main_menu(user['city'])
        return text, k

    async def menu(self, locations):
        text = await self._get(var_name="menu")
        k = await kb.menu(locations)
        return text, k

    async def balance(self, balance, rate, amount):
        text = await self._get(var_name="balance_message", balance=balance, amount=amount, rate=rate)
        k = await kb.deposit()
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

    async def account(self, account):
        text = await self._get(var_name='account', balance=float(account['balance']),
                               symbol=account['symbol']['name'].upper(), frozen=account['frozen'])
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

    async def symbol_market_buy(self, symbol, orders):
        text = await self._get(var_name='buy', symbol=symbol['name'].upper())
        k = await kb.symbol_market_buy(symbol, orders)
        return text, k

    async def symbol_market_sell(self, symbol, orders):
        text = await self._get(var_name='sell', symbol=symbol['name'].upper())
        k = await kb.symbol_market_buy(symbol, orders)
        return text, k

    async def symbol_broker_market_sell(self, symbol, broker, orders):
        text = await self._get(var_name='sell', symbol=symbol['name'].upper())
        k = await kb.symbol_broker_market_buy(symbol, orders)
        return text, k

    async def get_update_deposit(self, amount, symbol, **kwargs):
        text = await self._get(var_name='deposit_notification', symbol=symbol.upper(), amount=amount)
        k = None
        return text, k

    async def get_update_withdraw(self, link, **kwargs):
        text = await self._get(var_name='withdraw_notification', link=link)
        k = None
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
        text = await self._get(var_name=order['type'], symbol=order['symbol']['name'].upper())
        text += '\n\n'
        user = order.pop('user')
        text += await self._get(
            var_name='user',
            is_verify=verify_sm[user.pop('is_verify')],
            **user
        )
        text += '\n\n'
        text += await self._get(var_name='order', **order)
        if is_my:
            k = await kb.my_order(order)
        else:
            k = await kb.market_order(order['id'])
        return text, k

    async def user(self, user, is_admin):
        text = await self._get(var_name='user', is_verify=verify_sm[user.pop('is_verify')], **user)
        if is_admin:
            k = await kb.user_admin_actions(user)
        else:
            k = None
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


rc = ResponseComposer()
