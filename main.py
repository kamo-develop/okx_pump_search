import asyncio
import logging
from logging.handlers import RotatingFileHandler

from okx_api.api_client import ClientAPI
from candles_manager import CandlesManager
from pump_scanner import PumpScanner
from settings import activity_level, okx_url_trade
from signals import SignalManager
from tg_manager import TelegramManager
from trading.trading_manager import TradingManager

logger = logging.getLogger(__name__)

logging.basicConfig(
    handlers=[RotatingFileHandler('logs/i.log', maxBytes=2500000, backupCount=100)],
    level=logging.INFO,
    format=u'%(name)s %(funcName)s :%(lineno)d [%(asctime)s] #%(levelname)s - %(message)s',
)


def print_activity_to_log(sorted_activity, candles_manager: CandlesManager):
    i = 0
    for item in sorted_activity:
        instrument_name = item[0]
        activity = item[1]
        if activity > activity_level:
            logger.info(f"PUMP {okx_url_trade}/{instrument_name.lower()} act={round(activity, 2)}% price={candles_manager.get_last_candle(instrument_name).close}")
        i += 1
        if i >= 3:
            break


async def run(tg_manager: TelegramManager, pump_scanner: PumpScanner, trading_manager: TradingManager, client_api: ClientAPI, margin_instruments: set):
    candles_60_sec_manager = CandlesManager(60)
    signal_manager = SignalManager(tg_manager, margin_instruments, trading_manager)
    count_iteration = 0
    while True:
        try:
            tickers = await client_api.get_tickers('SPOT')
            tickers = tickers['data']
            for one_ticker in tickers:
                instrument_name = one_ticker['instId']
                quote_name = instrument_name.split('-')[1]
                if 'USDT' == quote_name:
                    last_price = float(one_ticker['last'])
                    candles_60_sec_manager.new_price(instrument_name, last_price)
                    await trading_manager.on_new_price(instrument_name, last_price)

            activity_60_sec = await pump_scanner.calc_activity(candles_60_sec_manager, signal_manager)
            # print_activity_to_log(activity_60_sec, candles_60_sec_manager)
            count_iteration += 1
            if count_iteration % 3000 == 0:
                logger.info("HOUR SLICE")
                pump_scanner.print_counts_to_log()
                pump_scanner.count_top_hits.send_to_tg(tg_manager)
            # elif count_iteration % 60 == 0:
            #     pump_scanner.print_counts_to_log(10)
            await asyncio.sleep(0.25)
        except Exception:
            logger.exception("Not processed Exception")


async def get_margin_instrument_set(client_api: ClientAPI):
    margin_instruments = set()
    instruments = (await client_api.get_instruments('MARGIN'))['data']
    for one_instrument in instruments:
        quote_name = one_instrument['instId'].split('-')[1]
        if 'USDT' == quote_name:
            margin_instruments.add(one_instrument['instId'])
    return margin_instruments


async def main(tg_manager: TelegramManager):
    client_api = ClientAPI()
    pump_scanner = PumpScanner()
    trading_manager = TradingManager(client_api)
    margin_instruments = await get_margin_instrument_set(client_api)
    task_tg = asyncio.create_task(tg_manager.run())
    task_scanner = asyncio.create_task(run(tg_manager, pump_scanner, trading_manager, client_api, margin_instruments))

    await task_tg
    await task_scanner


if __name__ == "__main__":
    tg_manager = TelegramManager()
    logger.info("START PROGRAM\n")
    tg_manager.on_start_up()
    try:
        asyncio.run(main(tg_manager))
    except KeyboardInterrupt:
        logger.info("FINISH PROGRAM")
        tg_manager.on_shut_down()
