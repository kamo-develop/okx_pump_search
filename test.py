import asyncio
import logging
from pprint import pprint

from pyrogram import Client

from api_client import ClientAPI
from settings import tg_api_id, tg_api_hash, tg_log_channel_id

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

asyncio.run(test_tg())


