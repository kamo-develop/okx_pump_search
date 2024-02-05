import logging

from candles_manager import CandlesManager, Candle
logger = logging.getLogger(__name__)

class Extremes:
    def __init__(self):
        pass

    def calc_last_minimum(self, candles: [Candle], max_candles=10) -> Candle:
        logger.info(f"count candles = {len(candles)}")
        if len(candles) == 1:
            return candles[0]

        if len(candles) == 2:
            if candles[-1].low <= candles[-2].low:
                return candles[-1]
            else:
                return candles[-2]

        for i in range(1, len(candles) - 1):
            if i > max_candles:
                return candles[-i]
            if candles[-i].low <= candles[-i - 1].low and candles[-i].low <= candles[-i - 2].low:
                return candles[-i]

        min_low = candles[0].low
        low_candle = candles[0]
        for candle in candles:
            if candle.low < min_low:
                min_low = candle.low
                low_candle = candle
        return low_candle

    def calc_last_maximum(self, candles: [Candle], max_candles=10) -> Candle:
        logger.info(f"count candles = {len(candles)}")
        if len(candles) == 1:
            return candles[0]

        if len(candles) == 2:
            if candles[-1].high >= candles[-2].high:
                return candles[-1]
            else:
                return candles[-2]

        for i in range(1, len(candles) - 1):
            if i > max_candles:
                return candles[-i]
            if candles[-i].high >= candles[-i - 1].high and candles[-i].high >= candles[-i - 2].high:
                return candles[-i]

        max_high = candles[0].high
        high_candle = candles[0]
        for candle in candles:
            if candle.high > max_high:
                max_high = candle.high
                high_candle = candle
        return high_candle
