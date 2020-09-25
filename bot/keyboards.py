from datetime import timedelta, datetime, timezone

from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
from dateutil.parser import parse

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

    async def confirm_policy(self):
        kb = self.get_kb([
            [self.label('confirm_policy')]
        ])
        return kb

    async def main_menu(self):
        kb = self.get_kb([
            [self.label('accounts'), self.label('trading')],
            [self.label('about'), self.label('settings')],
        ])
        return kb

    async def accounts(self, symbols, accounts):
        def get_balance(symbol_id):
            account = next(filter(lambda x: x['symbol']['id'] == symbol_id, accounts), None)
            return account['balance'] if account else None
        btns = []
        for symbol in symbols:
            name = symbol["name"].upper()
            balance = get_balance(symbol['id'])
            if balance:
                name += f' ({balance})'
            btns.append([self.inl_b(name, action=f'account {symbol["id"]}')])
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

    async def my_orders(self, orders, symbol):
        btns = [
            [
                self.inl_b(
                    f'{"ПОКУПКА" if order["type"] == "buy" else "ПРОДАЖА"} {order["broker"]}, '
                    f'{symbol["name"].upper()}, {prettify_number(order["limit_from"])}-{prettify_number(order["limit_to"])} ₽, {order["rate"]} ₽',
                    action=f'order {order["id"]}'
                )
            ]
            for order in orders
        ]
        btns.append([self.inl_b('new_order', action=f'new_order {symbol["id"]}')])
        btns.append([self.inl_b('back', action=f'market_choose_symbol {symbol["id"]}')])
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

    async def market_order(self, order_id, is_enough_money, is_requisites_filled, account_exists):
        if not account_exists:
            btns = [[self.inl_b('create_account_first', action='answer_only')]]
        elif not is_enough_money:
            btns = [[self.inl_b('not_enough_money', action='answer_only')]]
        elif not is_requisites_filled:
            btns = [[self.inl_b('fill_requisite', action='answer_only')]]
        else:
            btns = [[self.inl_b('begin_deal', action=f'begin_deal {order_id}')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def user_admin_actions(self, user):
        btns = [
            [self.inl_b('unverify' if user['is_verify'] else 'verify', action=f'verify {user["nickname"]}')],
            [self.inl_b('send_message', action=f'send_message {user["id"]}')]
        ]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def send_message(self, user):
        btns = [[self.inl_b('send_message', action=f'send_message {user["id"]}')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def symbol_market_action(self, symbol, brokers, action):
        btns = [
            [self.inl_b(f'✅ {broker["name"]} {broker["best_rate"]} ₽, ({broker["orders_cnt"]})',
                       action=f'broker_{action} {symbol["id"]} {broker["id"]}')]
            for broker in brokers if broker["best_rate"]
        ]
        btns.append([self.inl_b('back', action=f'market_choose_symbol {symbol["id"]}')])
        # btns = get_chunks(btns, 2)
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def symbol_broker_market(self, symbol, orders, action):
        btns = [
            [self.inl_b(f'{order["user"]}, {order["limit_from"]}-{order["limit_to"]} ₽, {order["rate"]}₽', action=f'order {order["id"]}')]
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

    async def settings(self, user):
        btns = [
            [self.inl_b('requisites', action='requisites')],
        ]
        if (
                (last_change := user['last_nickname_change']) is None
                or
                parse(last_change) + timedelta(days=30) < datetime.now(timezone.utc)
        ):
            btns.append([self.inl_b('nickname_change', action='nickname_change')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def requisites(self, brokers):
        btns = []
        for broker in brokers:
            btns.append(self.inl_b(broker['name'], action=f'requisite_broker {broker["id"]}'))
        btns = get_chunks(btns, 2)
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def broker_requisite(self, broker, requisite_exists):
        btns = [
            [self.inl_b('edit_requisite', action=f'edit_requisite {broker["id"]}')]
        ]
        if requisite_exists:
            btns.append([self.inl_b('edit_add_info', action=f'edit_add_info {broker["id"]}')])
        btns.append([self.inl_b('back', action='requisites')])
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

    async def send_crypto(self, deal_id, dispute):
        btns = [[self.inl_b('confirm_fiat', action=f'deal_send_crypto {deal_id}')]]
        if not dispute:
            btns.append([self.inl_b('open_dispute', action=f'open_dispute {deal_id}')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def open_dispute(self, deal_id):
        btns = [[self.inl_b('open_dispute', action=f'open_dispute {deal_id}')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def solve_dispute(self, deal_id):
        btns = [
            [self.inl_b('dispute_for_buyer', action=f'dispute_admin_buyer_win {deal_id}')],
            [self.inl_b('dispute_for_seller', action=f'dispute_admin_seller_win {deal_id}')]
        ]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def user_rate(self, deal_id):
        btns = [
            [
                self.inl_b('like', action=f'deal_like {deal_id}'),
                self.inl_b('dislike', action=f'deal_dislike {deal_id}')
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def get_cancel(self):
        return self.get_kb([['cancel']])

    async def are_you_sure(self):
        return self.get_kb([['yes', 'no']])


kb = Keyboard()
