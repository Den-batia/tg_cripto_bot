from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
from .translations.translations import translate
from .utils.utils import get_chunks

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
            [self.label('about')],
        ])
        return kb

    async def accounts(self, symbols):
        btns = [[self.inl_b(symbol['name'].upper(), action=f'account {symbol["id"]}')] for symbol in symbols]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def account(self, account):
        btns = [[
            self.inl_b('deposit', action=f'get_address {account["address"]}'),
            self.inl_b('withdraw', action=f'get_address {account["address"]}')
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
            [self.inl_b(f'{order["broker"]} {order["limit_from"]}-{order["limit_to"]}', action=f'')]
            for order in orders
        ]
        btns.append([self.inl_b('new_order', action=f'new_order {symbol_id}')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def symbol_market_buy(self, symbol, brokers):
        btns = [
            [self.inl_b(f'{broker["name"]} ({broker["orders_cnt"]})', action=f'broker_buy {symbol["id"]} {broker["id"]}')]
            for broker in brokers
        ]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def symbol_broker_market_buy(self, symbol, orders):
        btns = [
            [self.inl_b(f'{order["user"]}, {order["limit_from"]}-{order["limit_to"]}, {order["rate"]}', action=f'broker_buy {symbol["id"]} {order["id"]}')]
            for order in orders
        ]
        btns.append([self.inl_b(f'new_order')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def new_order_create(self, symbol_id):
        btns = [
            [self.inl_b(f'new_order_{order_type}', action=f'new_order {symbol_id} {order_type}')]
            for order_type in ['buy', 'sell']
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
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def get_link(self):
        btns = [[self.inl_b('invite_more', action='friends')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def ref(self):
        btns = [[self.inl_b('ref', action='ref')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def get_cancel(self):
        return self.get_kb([['cancel']])

    async def are_you_sure(self):
        return self.get_kb([['yes', 'no']])


kb = Keyboard()
