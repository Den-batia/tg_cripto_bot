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

    async def get_symbol(self, symbol_id):
        res = await self._call_api(f'/v1/symbols/{symbol_id}')
        return res

    async def get_broker(self, broker_id):
        res = await self._call_api(f'/v1/brokers/{broker_id}')
        return res

    async def get_brokers(self):
        res = await self._call_api('/v1/brokers')
        return res

    async def get_accounts(self, user_id):
        res = await self._call_api(f'/v1/accounts/{user_id}')
        return res

    async def get_aggregated_orders(self, symbol_id, order_type):
        res = await self._call_api(f'/v1/aggregated-orders/?symbol={symbol_id}&type={order_type}')
        return res

    async def get_orders(self, symbol_id, broker_id, order_type):
        res = await self._call_api(f'/v1/orders/?symbol={symbol_id}&type={order_type}&broker={broker_id}')
        return res

    async def get_user_orders(self, user_id, symbol_id):
        res = await self._call_api(f'/v1/users/{user_id}/orders?symbol={symbol_id}')
        return res

    async def create_account(self, user_id, symbol_id):
        res = await self._call_api(f'/v1/accounts/generate', method='post',
                                   _json={'user_id': user_id, 'symbol': symbol_id})
        return res

    async def check_address(self, address, symbol_id):
        res = await self._call_api(
            f'/v1/address-check', method='post',
            _json={'address': address, 'symbol': symbol_id}
        )
        return res

    async def create_withdraw(self, user_id, symbol_id, amount, address):
        res = await self._call_api(
            f'/v1/withdraws/new', method='post',
            _json={'user_id': user_id, 'symbol': symbol_id, 'amount': str(amount), 'address': address}
        )
        return res

    async def create_order(self, data):
        res = await self._call_api(f'/v1/orders/new', method='post', _json=data)
        return res

    async def get_user(self, user_tg_id):
        return await self._call_api(f'/v1/tg-users/{user_tg_id}')

    async def get_user_info(self, nickname):
        return await self._call_api(f'/v1/user-info/{nickname}')

    async def get_order_info(self, order_id):
        return await self._call_api(f'/v1/order-info/{order_id}')

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
