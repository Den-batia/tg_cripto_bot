from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
from .translations import translate
from .helpers import get_correct_value
from .settings import SUPPORT


LOT_ACTIVATION_STATUS = {True: '🌕', False: '🌑'}
LOT_USER_VERIFICATION_STATUS = {True: '✅', False: ''}
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

    async def main_menu(self, city=''):
        kb = self.get_kb([
            [self.label('balance')],
            [self.label('friends'), self.label('products', city=city)],
            [self.label('cities'), self.label('help')]
        ])
        return kb

    async def cities(self, cities):
        btns = [[self.inl_b(city, action=f'chosen_city {city}')] for city in cities]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def deposit(self, amount=None):
        action = 'deposit'
        if amount is not None:
            action += f' {amount}'
        btns = [[self.inl_b('deposit', action=action)]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def get_link(self):
        btns = [[self.inl_b('invite_more', action='friends')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def locations(self, locations: dict):
        btns = []
        for loc in locations:
            row = [self.inl_b(loc['loc_name'], action=f'location {loc["loc_id"]}')]
            if loc['can_delete']:
                row.append(self.inl_b('delete_icon', action=f'del_loc {loc["loc_id"]}'))
            btns.append(row)
        btns.append([self.inl_b('new', action='add_location')])
        btns.append([self.inl_b('back', action='menu')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def types(self, types):
        btns = []
        for t, cnt in types.items():
            btns.append([self.inl_b(f'{t} ({cnt})', action=f'menu_ptype {t}')])
        btns.append([self.inl_b('add_product', action='add_product')])
        btns.append([self.inl_b('back', action='menu')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def get_cancel(self):
        return self.get_kb([['cancel']])

    async def choose_type(self, types):
        btns = []
        for i in range(0, len(types), 2):
            btns.append([t for t in types[i:i + 2]])
        btns.append(['cancel'])
        return self.get_kb(btns)

    async def menu_chosen_type(self, location_products_cnt, p_type):
        btns = []
        for loc, cnt in location_products_cnt.items():
            btns.append([self.inl_b(f'{loc} ({cnt})', action=f'menu_ptype_city {p_type},{loc}')])
        btns.append([self.inl_b('back', action='product_settings')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def product_types(self, types):
        btns = []
        types = list(types)
        for t in types:
            btns.append([self.inl_b(f'{t}', action=f'chosen_ptype {t}')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def chosen_type(self, products):
        btns = []
        names = []
        for product in products:
            name = f'{product["type"]}, {product["name"]}'
            if name not in names:
                btns.append([self.inl_b(name, action=f'chosen_product {product["id"]}')])
                names.append(name)
        btns.append([self.inl_b('back', action='products')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def chosen_product(self, product):
        btns = [[self.inl_b('Купить', action=f'buy_product {product["id"]}')]]
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def are_you_sure(self):
        return self.get_kb([['yes', 'no']])

    async def menu_address(self, addresses):
        btns = []
        for a in addresses:
            btns.append([self.inl_b(a, action=f'address_info {a.id}')])
        btns.append([self.inl_b('back', action='')])
        return InlineKeyboardMarkup(inline_keyboard=btns)

    async def amounts(self):
        return self.get_kb([
            ['0.01', '0.05', '0.1', '0.3', '0.5', '0.7', '1'],
            ['Отмена']
        ])


kb = Keyboard()
