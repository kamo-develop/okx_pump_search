import json
import logging

from aiohttp import ClientSession
from okx import consts as c
from okx import utils

logger = logging.getLogger(__name__)


class RequestClient:

    def __init__(self, api_key='-1', api_secret_key='-1', passphrase='-1', flag='0',
                 base_api=c.API_URL, debug=False):
        self.API_KEY = api_key
        self.API_SECRET_KEY = api_secret_key
        self.PASSPHRASE = passphrase
        self.use_server_time = False
        self.flag = flag
        self.domain = base_api
        self.debug = debug

    async def _request(self, method, request_path, params):
        if method == c.GET:
            request_path = request_path + utils.parse_params_to_str(params)
        timestamp = utils.get_timestamp()
        body = json.dumps(params) if method == c.POST else ""
        if self.API_KEY != '-1':
            sign = utils.sign(utils.pre_hash(timestamp, method, request_path, str(body), self.debug),
                             self.API_SECRET_KEY).decode('utf-8')
            header = utils.get_header(self.API_KEY, sign, timestamp, self.PASSPHRASE, self.flag, self.debug)
        else:
            header = utils.get_header_no_sign(self.flag, self.debug)
        if self.debug:
            logger.info(f'domain: {self.domain}  '
                        f'url: {request_path}')

        if method == c.GET:
            async with ClientSession(base_url=self.domain) as session:
                async with session.get(url=request_path, headers=header) as response:
                    return await response.json()
        elif method == c.POST:
            async with ClientSession(base_url=self.domain) as session:
                async with session.post(url=request_path, headers=header, data=body) as response:
                    return await response.json()

