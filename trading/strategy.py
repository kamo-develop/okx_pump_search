import asyncio
import logging
from enum import Enum

from okx_api.api_client import ClientAPI

logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    PLACED = 1,
    CLOSED = 2,
    CANCELED = 3,

class Order:

    def __init__(self, order_id, price, quantity, side, time):
        self.order_id = order_id
        self.price = price
        self.quantity = quantity
        self.fill_size = 0.0
        self.fill_price = None
        self.side = side
        self.time = time
        self.status = OrderStatus.PLACED


class TraderStatus(Enum):
    STARTED = 0,
    PLACED_ORDER = 1,
    STOPPED = 2

class Strategy:
    def __init__(self, instrument_name, client_api: ClientAPI):
        self.instrument_name = instrument_name
        self.client_api = client_api

    async def amend_order_price(self, order_id, new_price):
        return await self._amend_order(order_id, new_price, '')

    async def amend_order_size(self, order_id, new_size):
        return await self._amend_order(order_id,'', new_size)

    async def _amend_order(self, order_id, new_price, new_size):
        for i in range(5):
            response_amend_order = (await self.client_api.amend_order(
                self.instrument_name, ordId=order_id,
                newPx=new_price, newSz=new_size
            ))['data']
            logger.debug(response_amend_order)
            if '0' == response_amend_order[0]['sCode']:
                order_id = response_amend_order[0]['ordId']
                return order_id
            else:
                logger.error(f"Fault in amending order {self.instrument_name}. {response_amend_order[0]['sMsg']}")
            await asyncio.sleep(0.5)
        return None

    async def place_order(self, side, order_price, order_quantity):
        for i in range(5):
            response_place_order = (await self.client_api.place_order(
                self.instrument_name,
                'cash', side, 'limit',
                order_quantity, px=order_price
            ))['data']
            logger.debug(response_place_order)
            if '0' == response_place_order[0]['sCode']:
                order_id = response_place_order[0]['ordId']
                return order_id
            else:
                logger.error(f"Fault in placing {side} order {order_quantity} {self.instrument_name} for {order_price}$. {response_place_order[0]['sMsg']}")
            await asyncio.sleep(0.5)
        return None

    async def place_market_order(self, side, order_quantity):
        for i in range(5):
            response_place_order = (await self.client_api.place_order(
                self.instrument_name,
                'cash', side, 'market',
                order_quantity
            ))['data']
            logger.debug(response_place_order)
            if '0' == response_place_order[0]['sCode']:
                order_id = response_place_order[0]['ordId']
                return order_id
            else:
                logger.error(f"Fault in placing {side} market order {order_quantity} {self.instrument_name}. {response_place_order[0]['sMsg']}")
            await asyncio.sleep(0.5)
        return None

    async def cancel_order(self, order_id) -> bool:
        for i in range(5):
            response_cancel_order = (await self.client_api.cancel_order(self.instrument_name, order_id))['data']
            logger.debug(response_cancel_order)
            if '0' == response_cancel_order[0]['sCode']:
                return True
            else:
                logger.error(f"Fault in cancel order {order_id} {self.instrument_name}. {response_cancel_order[0]['sMsg']}")
            await asyncio.sleep(0.5)
        return False


    async def get_order_detail(self, order_id):
        response_order_detail = (await self.client_api.get_order(self.instrument_name, order_id))['data']
        return response_order_detail[0]

    async def update_order(self, order: Order):
        buy_half_order_detail = await self.get_order_detail(order.order_id)
        if 'partially_filled' == buy_half_order_detail['state'] or 'filled' == buy_half_order_detail['state']:
            order.fill_size = float(buy_half_order_detail['accFillSz'])
            order.fill_price = buy_half_order_detail['fillPx']
            if 'filled' == buy_half_order_detail['state']:
                order.status = OrderStatus.CLOSED