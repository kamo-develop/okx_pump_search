import logging
import time

logger = logging.getLogger(__name__)

class Candle:
    def __init__(self, open_price):
        self.time = int(time.time())
        self.close = open_price
        self.open = open_price
        self.high = open_price
        self.low = open_price

    def update_close_price(self, new_price):
        self.close = new_price
        if new_price > self.high:
            self.high = new_price
        if new_price < self.low:
            self.low = new_price
class CandlesManager:
    def __init__(self, period):
        self.candles = dict()
        self.period = period

    def new_price(self, instrument_name, price):
        current_time = int(time.time())
        if instrument_name not in self.candles:
            self.candles[instrument_name] = list()
        if len(self.candles[instrument_name]) == 0:
            self.candles[instrument_name].append(Candle(price))
        if current_time - self.candles[instrument_name][-1].time > self.period:
            self.candles[instrument_name].append(Candle(price))
        self.candles[instrument_name][-1].update_close_price(price)

    def get_last_candle(self, instrument_name) -> Candle:
        return self.candles[instrument_name][-1]

    def get_candles(self, instrument_name) -> [Candle]:
        return self.candles[instrument_name]

    def print_candles_to_log(self):
        out = 'Candles:\n'
        for instrument_name, candles in self.candles.items():
            last_candle: Candle = candles[-1]
            out += f'{instrument_name} : {last_candle.time} open={last_candle.open} close={last_candle.close}\n'
        logger.info(out)



