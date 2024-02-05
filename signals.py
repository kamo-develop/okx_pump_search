import logging
import time

from candles_manager import CandlesManager
from settings import okx_url_trade
from tg_manager import TelegramManager
from trading.trading_manager import TradingManager
logger = logging.getLogger(__name__)

class Pump:

    def __init__(self, pump_force, average_force, count_force, pump_time):
        self.time = pump_time
        self.pump_force = pump_force
        self.average_force = average_force
        self.count_forces = count_force


class SignalManager:

    def __init__(self, tg_manager: TelegramManager, margin_instruments: set, trading_manager: TradingManager):
        self.pumps = dict()
        self.pump_duration = 300
        self.tg_manager = tg_manager
        self.margin_instruments = margin_instruments
        self.trading_manager = trading_manager

    async def new_pump(self, instrument_name, pump_force, average_force, count_forces, candles_manager: CandlesManager):
        if instrument_name not in self.pumps:
            self.pumps[instrument_name] = Pump(pump_force, average_force, count_forces, int(time.time()))
            logger.info(f"PUMP {okx_url_trade}/{instrument_name.lower()} act={round(pump_force, 2)}% price={candles_manager.get_last_candle(instrument_name).close}")
            self.tg_manager.on_new_pump(instrument_name, pump_force, average_force, count_forces, instrument_name in self.margin_instruments)
            await self.trading_manager.on_new_signal(instrument_name, candles_manager)
        else:
            self.pumps[instrument_name] = Pump(pump_force, average_force, count_forces, self.pumps[instrument_name].time)
            if int(time.time()) - self.pumps[instrument_name].time > self.pump_duration:
                self.pumps[instrument_name].time = int(time.time())
                logger.info(f"PUMP {okx_url_trade}/{instrument_name.lower()} act={round(pump_force, 2)}% price={candles_manager.get_last_candle(instrument_name).close}")
                self.tg_manager.on_new_pump(instrument_name, pump_force, average_force, count_forces, instrument_name in self.margin_instruments)
                await self.trading_manager.on_new_signal(instrument_name, candles_manager)
            else:
                pass




