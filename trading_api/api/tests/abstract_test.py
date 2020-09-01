from rest_framework.response import Response
from rest_framework.test import APITestCase, APIRequestFactory


class AbstractAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.uri = None
        self.view = None

    def _get_uri(self, **kwargs):
        raise NotImplementedError

    def _get_auth(self, token):
        return {'HTTP_AUTHORIZATION': f'Token {token}'}

    def _make_request(self, user, method, data=None, uri=None, view=None, **kwargs):
        uri = uri or self.uri
        auth = self._get_auth(user.token) if user else {}
        args = [uri] if method == 'get' else [uri, data]
        request = getattr(self.factory, method)(*args, **auth)
        view = view or self.view
        return view(request, **kwargs)

    def _make_get_request(self, user=None, uri=None, view=None, **kwargs) -> Response:
        return self._make_request(user, 'get', uri=uri, view=view, **kwargs)

    def _make_post_request(self, data, user=None, uri=None, **kwargs):
        return self._make_request(user, 'post', data=data, uri=uri, **kwargs)

    def _make_patch_request(self, data, user=None, uri=None, **kwargs):
        return self._make_request(user, 'patch', data=data, uri=uri, **kwargs)
