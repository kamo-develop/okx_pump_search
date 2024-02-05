import asyncio
import logging

from candles_manager import CandlesManager
from okx_api.api_client import ClientAPI
from settings import limit_count_trades, enable_trading
from trading.correction_hunter import CorrectionHunter

logger = logging.getLogger(__name__)

# Управляет запуском ботов, хранит их и передаёт им цену
class TradingManager:

    def __init__(self, client_api: ClientAPI):
        self.client_api = client_api
        self.traders = dict()

    # async def run(self):
    #     while True:
    #         for trader in self.traders.values():
    #             await trader.check_orders()
    #         await asyncio.sleep(0.25)

    def _clear_stopped_traders(self):
        removed_traders = list()
        for instr, trader in self.traders.items():
            if trader.is_stopped():
                removed_traders.append(instr)
        for instr in removed_traders:
            self.traders.pop(instr)
            logger.info(f"Trader on {instr} stopped."
                        f"Total number of traders is {len(self.traders)}")

    # Поступил новый сигнал
    async def on_new_signal(self, instrument_name, candles_manager: CandlesManager):
        if not enable_trading:
            return

        self._clear_stopped_traders()
        if len(self.traders) >= limit_count_trades:
            # Превышен лимит по количеству одновременно торгуемых валют
            logger.info(f"Too many ({len(self.traders)}) bots running at the same time. {instrument_name}")
            # todo: следить за этой валютой и если какой-то бот закончит работу, пытаться зайти по этой
            return

        if ((instrument_name in self.traders and self.traders[instrument_name].is_stopped())
                or instrument_name not in self.traders):
            new_trader = CorrectionHunter(instrument_name, candles_manager, self.client_api)
            await new_trader.start()
            self.traders[instrument_name] = new_trader

    async def on_new_price(self, instrument_name, new_price):
        if not enable_trading:
            return

        self._clear_stopped_traders()
        if instrument_name in self.traders:
            await self.traders[instrument_name].on_price_update(new_price)
            await self.traders[instrument_name].check_orders()
