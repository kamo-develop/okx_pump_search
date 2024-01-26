import configparser
import pathlib
import sys

script_dir = pathlib.Path(sys.argv[0]).parent
config_path = script_dir / 'config.ini'
config = configparser.ConfigParser()
config.read(config_path)

okx_api_key = config['okx']['api_key']
okx_api_secret = config['okx']['api_secret']
okx_api_passphrase = config['okx']['api_passphrase']
okx_url_trade = config['okx']['okx_url_trade']

tg_session_name = config['Telegram']['tg_session_name']
tg_signal_channel_id = int(config['Telegram']['tg_signal_channel_id'])
tg_log_channel_id = int(config['Telegram']['tg_log_channel_id'])

limit_funds = float(config['Trading']['limit_funds'])
activity_level = float(config['Trading']['activity_level'])
ma_period = int(config['Trading']['ma_period'])
limit_count_trades = int(config['Trading']['limit_count_trades'])

profit_levels = list(map(lambda level: float(level), config['Trading']['profit_levels'].split(',')))


