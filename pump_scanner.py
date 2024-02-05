import logging

from candles_manager import CandlesManager, Candle
from settings import activity_level
from signals import SignalManager
from tg_manager import TelegramManager

logger = logging.getLogger(__name__)


class Counter:
    def __init__(self):
        self.count = dict()

    def add_value(self, instrument_name, value):
        if instrument_name not in self.count:
            self.count[instrument_name] = {'count': 0, 'average': 0.0}
        total_sum = self.count[instrument_name]['average'] * self.count[instrument_name]['count']
        total_sum += value
        self.count[instrument_name]['count'] += 1
        self.count[instrument_name]['average'] = total_sum / self.count[instrument_name]['count']

    def print_counts_to_log(self, count_items=None):
        sorted_by_count = sorted(self.count.items(), key=lambda item: item[1]['count'], reverse=True)
        # sorted_by_average = sorted(self.count.items(), key=lambda item: item[1]['average'], reverse=True)
        if count_items is None:
            count_items = len(self.count)
        count_items = min(len(self.count), count_items)
        out = ''
        for i in range(count_items):
            instrument_name = sorted_by_count[i][0]
            value = sorted_by_count[i][1]
            out += f"{instrument_name} ~ ({value['count']}, {round(value['average'], 2)}%); "
        logger.info(f'{out}')

        # out = ''
        # for i in range(count_items):
        #     instrument_name = sorted_by_average[i][0]
        #     value = sorted_by_average[i][1]
        #     out += f"{instrument_name} ~ ({round(value['average'], 2)}, {value['count']}); "
        # logger.info(f'{out}')

    def send_to_tg(self, tg_manager: TelegramManager):
        sorted_by_count = sorted(self.count.items(), key=lambda item: item[1]['count'], reverse=True)
        tg_manager.on_statistic(sorted_by_count)


class PumpScanner:
    def __init__(self, count_top=3):
        self.count_top = count_top
        self.count_top_hits = Counter()
        self.count_pumps = Counter()

    async def calc_activity(self, candles_manager: CandlesManager, signal_manager: SignalManager):
        activity = dict()
        pump_list = list()
        for instrument_name, candles in candles_manager.candles.items():
            last_candle: Candle = candles[-1]
            activity[instrument_name] = (last_candle.close / last_candle.open - 1) * 100

            if abs(activity[instrument_name]) > activity_level:
                self.count_pumps.add_value(instrument_name, activity[instrument_name])
                pump_list.append(instrument_name)

        sorted_activity = sorted(activity.items(), key=lambda item: item[1], reverse=True)
        for i in range(self.count_top):
            if sorted_activity[i][1] != 0:
                self.count_top_hits.add_value(sorted_activity[i][0], sorted_activity[i][1])
        for instrument_name in pump_list:
            instrument_stat = self.count_top_hits.count.get(instrument_name,
                                                            {
                                                                'average': 0,
                                                                'count': 0,
                                                            })
            await signal_manager.new_pump(
                instrument_name, activity.get(instrument_name, 0),
                instrument_stat['average'], instrument_stat['count'],
                candles_manager)
        return sorted_activity

    def print_counts_to_log(self, count_items=None):
        logger.info('Counts TOP HINTS:')
        self.count_top_hits.print_counts_to_log(count_items)
        logger.info('Counts PUMPS:')
        self.count_pumps.print_counts_to_log(count_items)
        logger.info('\n')


