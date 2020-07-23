from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
from .translations.translations import translate

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
