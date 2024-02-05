import asyncio
import logging
import os
from pprint import pprint

from pyrogram import Client

from okx_api.api_client import ClientAPI
from settings import tg_log_channel_id, okx_api_key, enable_trading

logging.basicConfig(
    level=logging.INFO,
    format=u'%(name)s %(funcName)s :%(lineno)d [%(asctime)s] #%(levelname)s - %(message)s',
)


logger = logging.getLogger(__name__)

client_api = ClientAPI()

async def run():
    instrument_name = 'BRWL-USDT'
    logger.info('Start test')
    response_place_order = (await client_api.place_order(instrument_name, 'cash', 'buy', 'limit', 90, px=0.015803999999))['data']
    if 0 != response_place_order[0]['sCode']:
        logger.error(response_place_order[0]['sMsg'])

    order_id = response_place_order[0]['ordId']
    logger.info(f"Response: {order_id}")
    pprint(response_place_order)

    response_cancel_order = await client_api.cancel_order(instrument_name, order_id)
    logger.info(f"Response cancel")
    pprint(response_cancel_order)


async def test_tg():
    tg_app = Client('ServerApp')
    async with tg_app:
        await tg_app.send_message(tg_log_channel_id, "HI")

def test_dotenv():
    print(type(enable_trading))
    print(enable_trading)


def test_list():
    ls = [1, 2, 3, 4, 5]
    for i in range(1, len(ls) - 1):
        print(f"{ls[-i]}  {ls[-i-1]}  {ls[-i-2]}" )

test_dotenv()

