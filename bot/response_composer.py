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

    async def cancel(self):
        text = await self._get(var_name="cancel_message")
        k = await kb.main_menu()
        return text, k

    async def get_main_k(self):
        return await kb.main_menu()

    async def unknown_error(self):
        text = await self._get(var_name='unknown_error')
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
        text = await self._get(var_name='account')
        k = await kb.account(account)
        return text, k


rc = ResponseComposer()
