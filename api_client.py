from okx.consts import *

from request_client import RequestClient
from settings import okx_api_key, okx_api_secret, okx_api_passphrase


class ClientAPI(RequestClient):
    def __init__(self):
        RequestClient.__init__(self, okx_api_key, okx_api_secret, okx_api_passphrase)

    async def get_tickers(self, instType, instFamily=''):
        params = {'instType': instType, 'instFamily': instFamily}
        return await self._request(GET, TICKERS_INFO, params)


    # Get Instruments
    async def get_instruments(self, instType, uly='', instId='', instFamily=''):
        params = {'instType': instType, 'uly': uly, 'instId': instId, 'instFamily': instFamily}
        return  await self._request(GET, INSTRUMENT_INFO, params)

    async def get_balances(self, ccy=''):
        params = {'ccy': ccy}
        return await self._request(GET, GET_BALANCES, params)

    async def get_deposit_history(self, ccy='', state='', after='', before='', limit='', txId='', depId='', fromWdId=''):
        params = {'ccy': ccy, 'state': state, 'after': after, 'before': before, 'limit': limit, 'txId': txId,
                  'depId': depId, 'fromWdId': fromWdId}
        return await self._request(GET, DEPOSIT_HISTORIY, params)

    # Place Order
    async def place_order(self, instId, tdMode, side, ordType, sz, ccy='', clOrdId='', tag='', posSide='', px='',
                    reduceOnly='', tgtCcy='', tpTriggerPx='', tpOrdPx='', slTriggerPx='', slOrdPx='',
                    tpTriggerPxType='', slTriggerPxType='', quickMgnType='', stpId='', stpMode=''):
        params = {'instId': instId, 'tdMode': tdMode, 'side': side, 'ordType': ordType, 'sz': sz, 'ccy': ccy,
                  'clOrdId': clOrdId, 'tag': tag, 'posSide': posSide, 'px': px, 'reduceOnly': reduceOnly,
                  'tgtCcy': tgtCcy, 'tpTriggerPx': tpTriggerPx, 'tpOrdPx': tpOrdPx, 'slTriggerPx': slTriggerPx,
                  'slOrdPx': slOrdPx, 'tpTriggerPxType': tpTriggerPxType, 'slTriggerPxType': slTriggerPxType,
                  'quickMgnType': quickMgnType, 'stpId': stpId, 'stpMode': stpMode}
        return await self._request(POST, PLACR_ORDER, params)

    # Cancel Order
    async def cancel_order(self, instId, ordId='', clOrdId=''):
        params = {'instId': instId, 'ordId': ordId, 'clOrdId': clOrdId}
        return await self._request(POST, CANCEL_ORDER, params)

