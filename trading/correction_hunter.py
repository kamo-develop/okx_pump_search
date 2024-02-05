import asyncio
import logging
import time
from enum import Enum

from candles_manager import CandlesManager
from okx_api.api_client import ClientAPI
from settings import limit_funds, fee, buy_half_level, close_high_level, critical_loss_zone, second_loss_zone, \
    first_loss_zone, critical_loss_time, second_loss_time, first_loss_time
from trading.indicators import Extremes
from trading.strategy import Strategy, TraderStatus, Order, OrderStatus

logger = logging.getLogger(__name__)




class CorrectionHunter(Strategy):

    def __init__(self, instrument_name, candles_manager: CandlesManager, client_api: ClientAPI):
        super().__init__(instrument_name, client_api)
        self.min_quantity = 0.0
        self.candles_manager = candles_manager
        self.extremes_indicator = Extremes()

        candles = self.candles_manager.get_candles(self.instrument_name)
        self.start_pump_price = self.extremes_indicator.calc_last_minimum(candles).low
        self.max_price = self.extremes_indicator.calc_last_maximum(candles).high
        self.max_purchase_price = self.max_price

        self.status = TraderStatus.STARTED
        self.buy_half_order: Order = None
        self.close_order: Order = None

        self.first_loss_timer = None
        self.second_loss_timer = None
        self.critical_loss_timer = None

    # Обновляет состояние выставленных заявок
    async def check_orders(self):
        if self.buy_half_order is not None:
            await self.update_order(self.buy_half_order)

        if self.close_order is not None:
            await self.update_order(self.close_order)

        if self.buy_half_order.fill_size > 0:
            self.max_purchase_price = self.max_price
            if self.close_order is None:
                logger.info(f"I bought {self.buy_half_order.fill_size} {self.instrument_name} for {self.buy_half_order.fill_price}$ ")
                order_price = self._calc_close_price()
                order_quantity = self.buy_half_order.fill_size * (1 - fee)
                logger.info(f"Im going to place sell order {order_quantity} {self.instrument_name} for {order_price}$")
                order_id = await self.place_order('sell', order_price, order_quantity)
                if order_id is not None:
                    self.close_order = Order(order_id, order_price, order_quantity, 'sell', int(time.time()))
                    logger.info(f"I placed sell order {order_quantity} {self.instrument_name} for {order_price}$")

            # учитывая минимальный размер заявки
            elif self._calc_base_balance() > self.min_quantity:
                new_quantity = self._calc_base_balance()
                logger.info(f"I bought {new_quantity} additional {self.instrument_name} for {self.buy_half_order.fill_price}$ ")
                logger.info(f"Im going to amend quantity sell order {new_quantity} {self.instrument_name} for {self.close_order.price}$")
                order_id = await self.amend_order_size(self.close_order.order_id, new_quantity)
                if order_id is not None:
                    logger.info(f"I amended quantity sell order {new_quantity} {self.instrument_name} for {self.close_order.price}$")
                    self.close_order.quantity += new_quantity
                    self.close_order.status = OrderStatus.PLACED

        # Окончание работы бота, если обе заявки полностью исполнены и нет незакрытого количества валюты
        if self.buy_half_order is not None and self.close_order is not None:
            if OrderStatus.CLOSED == self.close_order.status and OrderStatus.CLOSED == self.buy_half_order.status\
                    and self._calc_base_balance() <= self.min_quantity:
                self.status = TraderStatus.STOPPED



    # Принятие решений на основне изменения цены
    async def on_price_update(self, new_price):
        # Пока ордер на покупку не полностью исполнен, продолжаем двигать его при необходимости
        if OrderStatus.PLACED == self.buy_half_order.status:
            if new_price > self.max_price:
                self.max_price = new_price
                logger.info(f"New max price {self.max_price} on {self.instrument_name}")
                new_buy_price = self._calc_buy_half_price()
                if new_buy_price / self.buy_half_order.price - 1 > 0.001:
                    # todo: возможно стоит менять объем заявки, так как при увеличении цены usdt растет
                    logger.info(f"Im going amend buy order {self.buy_half_order.quantity} {self.instrument_name} "
                                f"for {new_buy_price}$")
                    order_id = await self.amend_order_price(self.buy_half_order.order_id, new_buy_price)
                    if order_id is not None:
                        logger.info(f"I amended buy order {self.buy_half_order.quantity} {self.instrument_name} "
                                    f"for {self.buy_half_order.price}$ -> {new_buy_price}$")
                        self.buy_half_order.price = new_buy_price

        await self.risk_management(new_price)

    async def risk_management(self, new_price):
        self.start_loss_timer(new_price)
        await self.check_loss_timer(new_price)

    def start_loss_timer(self, new_price):
        if new_price <= self._calc_loss_price(critical_loss_zone):
            # Сохранение времени пересечения цены уровня риска
            if self.critical_loss_timer is None:
                self.critical_loss_timer = int(time.time())
                logger.info(f"Price {new_price} on {self.instrument_name} BELOW critical loss level {self._calc_loss_price(critical_loss_zone)}")
        elif self.critical_loss_timer is not None:
            # Сброс таймера
            self.critical_loss_timer = None     # todo: возможно сбрасывать тоже стоит через время?
            logger.info(f"Price {new_price} on {self.instrument_name} above again critical loss level {self._calc_loss_price(critical_loss_zone)}")

        if new_price <= self._calc_loss_price(second_loss_zone):
            if self.second_loss_timer is None:
                logger.info(f"Price {new_price} on {self.instrument_name} BELOW second loss level {self._calc_loss_price(second_loss_zone)}")
                self.second_loss_timer = int(time.time())
        elif self.second_loss_timer is not None:
            self.second_loss_timer = None
            logger.info(f"Price {new_price} on {self.instrument_name} above again second loss level {self._calc_loss_price(second_loss_zone)}")

        if new_price <= self._calc_loss_price(first_loss_zone):
            if self.first_loss_timer is None:
                logger.info(f"Price {new_price} on {self.instrument_name} BELOW first loss level {self._calc_loss_price(first_loss_zone)}")
                self.first_loss_timer = int(time.time())
        elif self.first_loss_timer is not None:
            logger.info(f"Price {new_price} on {self.instrument_name} above again first loss level {self._calc_loss_price(first_loss_zone)}")
            self.first_loss_timer = None

    async def check_loss_timer(self, new_price):
        cur_time = int(time.time())
        if self.critical_loss_timer is not None and cur_time - self.critical_loss_timer > critical_loss_time:
            logger.info(f"CRITICAL ({critical_loss_zone}) loss level {new_price} on {self.instrument_name} {cur_time - self.critical_loss_timer} sec")
            await self.close_loss_position()

        if self.second_loss_timer is not None and cur_time - self.second_loss_timer > second_loss_time:
            logger.info(f"Second ({second_loss_zone}) loss level {new_price} on {self.instrument_name} {cur_time - self.second_loss_timer} sec")

        if self.first_loss_timer is not None and cur_time - self.first_loss_timer > first_loss_time:
            logger.info(f"First ({first_loss_zone}) loss level {new_price} on {self.instrument_name} {cur_time - self.first_loss_timer} sec")

    async def close_loss_position(self):
        if self.buy_half_order is not None and self.buy_half_order.status == OrderStatus.PLACED:
            logger.warning(f"There is buy half order when stop loss triggered. "
                           f"Im going to cancel buy order {self.buy_half_order.quantity} {self.instrument_name} for {self.buy_half_order.price}$")
            order_canceled = await self.cancel_order(self.buy_half_order.order_id)
            if order_canceled:
                self.buy_half_order.status = OrderStatus.CANCELED
                logger.info(f"I canceled buy order {self.buy_half_order.quantity} {self.instrument_name} for {self.buy_half_order.price}$")

        if self.close_order is not None and self.close_order.status == OrderStatus.PLACED:
            logger.info(f"Im going to cancel sell order {self.close_order.quantity} {self.instrument_name} for {self.close_order.price}$")
            order_canceled = await self.cancel_order(self.close_order.order_id)
            if order_canceled:
                self.close_order.status = OrderStatus.CANCELED
                logger.info(f"I canceled sell order {self.close_order.quantity} {self.instrument_name} for {self.close_order.price}$")

        logger.info(f"Im going to close position {self._calc_base_residual()} {self.instrument_name}")
        order_market_id = await self.place_market_order('sell', self._calc_base_residual())
        if order_market_id is not None:
            self.status = TraderStatus.STOPPED
            logger.info(f"I closed position {self._calc_base_residual()} {self.instrument_name}")





    async def start(self):
        logger.info(f"Start Correction Hunter on {self.instrument_name}")

        instrument = (await self.client_api.get_instruments('SPOT', instId=self.instrument_name))['data'][0]
        self.min_quantity = float(instrument['minSz'])

        logger.info(f"start_pump_price={self.start_pump_price}  max_price={self.max_price}  on {self.instrument_name}")

        order_price = self._calc_buy_half_price()
        order_quantity = limit_funds / order_price
        if order_quantity < self.min_quantity:
            order_quantity = self.min_quantity * 1.1
        logger.info(f"Im going to place buy order {order_quantity} {self.instrument_name} for {order_price}$")
        order_id = await self.place_order('buy', order_price, order_quantity)
        if order_id is None:
            self.status = TraderStatus.STOPPED
            return
        self.buy_half_order = Order(order_id, order_price, order_quantity, 'buy', int(time.time()))
        self.status = TraderStatus.PLACED_ORDER
        logger.info(f"I placed buy order {order_quantity} {self.instrument_name} for {order_price}$")

    def _calc_base_balance(self):
        # todo: Учитывать комисиию нормально или брать объём с баланса
        return (self.buy_half_order.fill_size - self.close_order.quantity) * (1 - fee)

    # Остаточный объём для закрытия позиции по рынку
    def _calc_base_residual(self):
        return (self.buy_half_order.fill_size - self.close_order.fill_size) * (1 - fee)

    def _calc_loss_price(self, zone):
        range_size = self.max_purchase_price - self.start_pump_price
        return range_size * zone + self.start_pump_price

    def _calc_buy_half_price(self):
        range_size = self._calc_range_size()
        return range_size * buy_half_level + self.start_pump_price

    def _calc_close_price(self):
        range_size = self._calc_range_size()
        return range_size * close_high_level + self.start_pump_price

    def _calc_range_size(self):
        return self.max_price - self.start_pump_price

    def is_stopped(self):
        return TraderStatus.STOPPED == self.status


