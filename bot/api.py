import aiohttp

from .settings import API_HOST


class API:
    async def _call_api(self, address, method='get', _json=None, api_url=True, is_photo=False):
        host = (API_HOST if not api_url else API_HOST + '/api') + address
        headers = {'Content-Type': 'application/json', 'Host': 'null'}
        async with aiohttp.ClientSession() as session:
            if method == 'get':
                resp = await session.get(host, headers=headers)
            else:
                resp = await getattr(session, method)(host, json=_json, headers=headers)

            try:
                resp.raise_for_status()
            except Exception:
                print(await resp.json())
                raise

            if is_photo:
                return await resp.read()

            if resp.status != 204:
                return await resp.json()

    async def get_rate(self):
        res = await self._call_api(f'/v1/rate')
        return res['rate']

    async def get_symbols(self):
        res = await self._call_api(f'/v1/symbols')
        return res

    async def get_accounts(self, user_id):
        res = await self._call_api(f'/v1/accounts/{user_id}')
        return res

    async def create_account(self, user_id, symbol):
        res = await self._call_api(f'/v1/accounts/generate', method='post', _json={'user_id': user_id, 'symbol': symbol})
        return res

    async def get_user(self, user_tg_id):
        return await self._call_api(f'/v1/tg-users/{user_tg_id}')

    async def get_text(self, name):
        res = await self._call_api(f'/v1/texts/{name}')
        return res['text']

    async def update_user(self, user_tg_id, data):
        return await self._call_api(f'/v1/tg-users/{user_tg_id}/', method='patch', _json=data)

    async def register_user(self, user_tg_id, ref_code):
        body = {'telegram_id': user_tg_id}
        if ref_code is not None:
            body['ref'] = ref_code
        return await self._call_api(f'/v1/tg-users/new', method='post', _json=body)


api = API()
