from .api import api
from .keyboards import kb
from .settings import SHOP_NAME, SUPPORT, SYMBOL

verify_sm = {True: '✅', False: '❌'}


lang = 'ru'


class ResponseComposer:
    async def _get(self, *, var_name, **kwargs):
        kwargs['symbol'] = SYMBOL.upper()
        kwargs['support'] = SUPPORT
        kwargs['shop_name'] = SHOP_NAME
        text: str = await api.get_text(var_name)
        return text.format(**kwargs).expandtabs(2)

    async def _big_number_str(self, value):
        return "{:,}".format(value)

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

    async def cities(self, cities):
        text = await self._get(var_name="cities_header")
        k = await kb.cities(cities)
        return text, k

    async def selected_city(self, user):
        text = await self._get(var_name="selected_city", city=user['city'])
        k = await kb.main_menu(user['city'])
        return text, k

    async def products(self, user):
        text = await self._get(var_name="product_message")
        k = await kb.main_menu(user['city'])
        return text, k

    async def balance(self, balance, rate, amount):
        text = await self._get(var_name="balance_message", balance=balance, amount=amount, rate=rate)
        k = await kb.deposit()
        return text, k

    async def done(self):
        text = await self._get(var_name="done")
        k = await kb.main_menu()
        return text, k

    async def cancel(self):
        text = await self._get(var_name="cancel_message")
        k = await kb.main_menu()
        return text, k

    async def get_main_k(self):
        return await kb.main_menu()


rc = ResponseComposer()
