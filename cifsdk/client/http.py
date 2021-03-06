import logging
import requests
import time
import json
from cifsdk.exceptions import AuthError, TimeoutError, NotFound, SubmissionFailed
from cifsdk.constants import VERSION
from pprint import pprint
import zlib
from base64 import b64decode
import binascii
from cifsdk.client.plugin import Client
import os

requests.packages.urllib3.disable_warnings()

TRACE = os.environ.get('CIFSDK_CLIENT_HTTP_TRACE')

logger = logging.getLogger(__name__)

logger.setLevel(logging.ERROR)

if TRACE:
    logger.setLevel(logging.DEBUG)


class HTTP(Client):

    def __init__(self, remote, token, proxy=None, timeout=300, verify_ssl=True, **kwargs):
        super(HTTP, self).__init__(remote, token, **kwargs)

        self.proxy = proxy
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.nowait = kwargs.get('nowait', False)

        self.session = requests.Session()
        self.session.headers["Accept"] = 'application/vnd.cif.v3+json'
        self.session.headers['User-Agent'] = 'cifsdk-py/{}'.format(VERSION)
        self.session.headers['Authorization'] = 'Token token=' + self.token
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['Accept-Encoding'] = 'gzip'

    def _check_status(self, resp, expect=200):
        if resp.status_code == 401:
            raise AuthError()

        if resp.status_code == 404:
            raise NotFound()

        if resp.status_code == 408:
            raise TimeoutError()

        if resp.status_code == 422:
            raise SubmissionFailed()

        if resp.status_code != expect:
            raise RuntimeError(resp.content)

    def _get(self, uri, params={}):
        if not uri.startswith('http'):
            uri = self.remote + uri

        resp = self.session.get(uri, params=params, verify=self.verify_ssl)

        self._check_status(resp, expect=200)

        data = resp.content
        try:
            data = zlib.decompress(b64decode(data))
        except (TypeError, binascii.Error) as e:
            pass
        except Exception as e:
            pass

        msgs = json.loads(data.decode('utf-8'))

        if not msgs.get('status') and not msgs.get('message') == 'success':
            raise RuntimeError(msgs)

        if msgs.get('status') and msgs['status'] == 'failure':
            raise InvalidSearch(msgs['message'])

        if isinstance(msgs.get('data'), list):
            for m in msgs['data']:
                if m.get('message'):
                    try:
                        m['message'] = b64decode(m['message'])
                    except Exception as e:
                        pass
        return msgs

    def _post(self, uri, data):
        if type(data) == dict:
            data = json.dumps(data)

        if self.nowait:
            uri = '{}?nowait=1'.format(uri)

        resp = self.session.post(uri, data=data, verify=self.verify_ssl)

        self._check_status(resp, expect=201)

        return json.loads(resp.content.decode('utf-8'))

    def _delete(self, uri, data):
        resp = self.session.delete(uri, data=json.dumps(data))
        self._check_status(resp)
        return json.loads(resp.content)

    def _patch(self, uri, data):
        resp = self.session.patch(uri, data=json.dumps(data))
        self._check_status(resp)
        return json.loads(resp.content)

    def indicators_search(self, filters):
        rv = self._get('/search', params=filters)
        return rv['data']

    def indicators_create(self, data):
        data = str(data).encode('utf-8')

        uri = "{0}/indicators".format(self.remote)
        logger.debug(uri)
        rv = self._post(uri, data)
        return rv["data"]

    def feed(self, filters):
        rv = self._get('/feed', params=filters)
        return rv['data']

    def ping(self, write=False):
        t0 = time.time()

        uri = '/ping'
        if write:
            uri = '/ping?write=1'

        rv = self._get(uri)

        if rv:
            rv = (time.time() - t0)
            logger.debug('return time: %.15f' % rv)

        return rv

    def tokens_search(self, filters):
        rv = self._get('{}/tokens'.format(self.remote), params=filters)
        return rv['data']

    def tokens_delete(self, data):
        rv = self._delete('{}/tokens'.format(self.remote), data)
        return rv['data']

    def tokens_create(self, data):
        logger.debug(data)
        rv = self._post('{}/tokens'.format(self.remote), data)
        return rv['data']

    def tokens_edit(self, data):
        rv = self._patch('{}/tokens'.format(self.remote), data)
        return rv['data']

Plugin = HTTP
