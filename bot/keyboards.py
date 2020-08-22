from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
from .translations.translations import translate
from .utils.utils import get_chunks, prettify_number

lang = 'ru'


class Keyboard:
    def inl_b(self, name, action=None, link=None, **kwargs):
        if link is not None:
            return InlineKeyboardButton(self.label(name, **kwargs), url=link)

        elif action is not None:
            return InlineKeyboardButton(self.label(name, **kwargs), callback_data=action)

        else:
            return InlineKeyboardButton(self.label(name, **kwargs), callback_data=name)

    def label(self, name, **kwargs):
        t = translate(f'menu_misc.{name}', locale=lang, **kwargs)
        if 'menu_misc' in t:
            return name
        else:
            return t

    def get_kb(self, btns):
        formed_btns = []
        for row in btns:
            formed_btns.append([self.label(name) for name in row])
        return ReplyKeyboardMarkup(formed_btns, resize_keyboard=True)

    def get_btns_for_ik(self, btns):
        formed_btns = []
        for row in btns:
            formed_btns.append([self.inl_b(name) for name in row])
        return formed_btns

    async def main_menu(self):
        kb = self.get_kb([
            [self.label('accounts'), self.label('trading')],
            [self.label('about'), self.label('requisites')],
        ])
        return kb

    async def accounts(self, symbols):
        btns = [[self.inl_b(symbol['name'].upper(), action=f'account {symbol["id"]}')] for symbol in symbols]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def account(self, account):
        btns = [[
            self.inl_b('deposit', action=f'get_address {account["address"]}'),
            self.inl_b('withdraw', action=f'withdraw {account["symbol"]["id"]}')
        ]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def create_account(self, symbol_id):
        btns = [[self.inl_b('create_account', action=f'create_account {symbol_id}')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def market_choose_symbol(self, symbols):
        btns = [[self.inl_b(symbol['name'].upper(), action=f'market_choose_symbol {symbol["id"]}') for symbol in symbols]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def symbol_market(self, symbol):
        btns = [
            [self.inl_b('buy', action=f'buy {symbol["id"]}'), self.inl_b('sell', action=f'sell {symbol["id"]}')],
            [self.inl_b('my_orders', action=f'my_orders {symbol["id"]}')]
        ]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def my_orders(self, orders, symbol_id):
        btns = [
            [
                self.inl_b(
                    f'{"📈" if order["type"] == "buy" else "📉"} {order["broker"]}, '
                    f'{prettify_number(order["limit_from"])}-{prettify_number(order["limit_to"])}, {order["rate"]} RUB',
                    action=f'order {order["id"]}'
                )
            ]
            for order in orders
        ]
        btns.append([self.inl_b('new_order', action=f'new_order {symbol_id}')])
        btns.append([self.inl_b('back', action=f'market_choose_symbol {symbol_id}')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def my_order(self, order):
        btns = [
            [
                self.inl_b('limits', action=f'order_edit_limits {order["id"]}'),
                self.inl_b('rate', action=f'order_edit_rate {order["id"]}'),
                self.inl_b('details', action=f'order_edit_details {order["id"]}'),
            ],
            [
                self.inl_b('back', action=f'my_orders {order["symbol"]["id"]}'),
                self.inl_b('delete', action=f'order_edit_delete {order["id"]}'),
                self.inl_b('deactivate' if order['is_active'] else 'activate', action=f'order_edit_activity {order["id"]}')
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def market_order(self, order_id):
        btns = [[self.inl_b('begin_deal', action=f'begin_deal {order_id}')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def user_admin_actions(self, user):
        btns = [
            [
                self.inl_b('unverify' if user['is_verify'] else 'verify', action=f'verify {user["nickname"]}')
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def send_message(self, user):
        btns = [[self.inl_b('send_message', action=f'send_message {user["id"]}')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def symbol_market_action(self, symbol, brokers, action):
        btns = [
            self.inl_b(f'{broker["name"]} ({broker["orders_cnt"]})', action=f'broker_{action} {symbol["id"]} {broker["id"]}')
            for broker in brokers
        ]
        btns = get_chunks(btns, 2)
        btns.append([self.inl_b('back', action=f'market_choose_symbol {symbol["id"]}')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def symbol_broker_market(self, symbol, orders, action):
        btns = [
            [self.inl_b(f'{order["user"]}, {order["limit_from"]}-{order["limit_to"]} RUB, {order["rate"]}', action=f'order {order["id"]}')]
            for order in orders
        ]
        btns.append([self.inl_b('back', action=f'{action} {symbol["id"]}')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def new_order_create(self, symbol_id):
        btns = [
            [
                self.inl_b(f'new_order_{order_type}', action=f'new_order_brokers {symbol_id} {order_type}')
                for order_type in ['buy', 'sell']
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def get_new_brokers(self, brokers, chosen_brokers):
        brokers_list = []
        for broker in brokers:
            is_exists = broker["id"] in chosen_brokers
            btn = self.inl_b(
                f'{"✅" if is_exists else "❌"} {broker["name"]}',
                action=f'{"remove" if is_exists else "add"} broker {broker["id"]}'
            )
            brokers_list.append(btn)
        btns = get_chunks(brokers_list, 2)
        controls = [self.inl_b('cancel', action='cancel')]
        if chosen_brokers:
            controls.append(self.inl_b('done', action='done'))
        btns.append(controls)
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def get_link(self):
        btns = [[self.inl_b('invite_more', action='friends')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def ref(self):
        btns = [[self.inl_b('ref', action='ref')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def requisites(self, brokers):
        btns = []
        for broker in brokers:
            btns.append(self.inl_b(broker['name'], action=f'requisite_broker {broker["id"]}'))
        btns = get_chunks(btns, 2)
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def broker_requisite(self, broker):
        btns = [[self.inl_b('edit_requisite', action=f'edit_requisite {broker["id"]}')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def confirm_deal(self, deal_id):
        btns = [
            [
                self.inl_b('confirm', action=f'confirm_deal {deal_id}'),
                self.inl_b('decline', action=f'decline_deal {deal_id}')
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def send_fiat(self, deal_id):
        btns = [[self.inl_b('fiat_sent', action=f'deal_send_fiat {deal_id}')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def send_crypto(self, deal_id):
        btns = [[self.inl_b('confirm_fiat', action=f'deal_send_crypto {deal_id}')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def get_cancel(self):
        return self.get_kb([['cancel']])

    async def are_you_sure(self):
        return self.get_kb([['yes', 'no']])


kb = Keyboard()
