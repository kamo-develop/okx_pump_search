import os
from dotenv import load_dotenv

load_dotenv()

# todo: переделать settings в класс с методами, чтобы при обращении к параметру, каждый раз вытягивать его из env
okx_api_key = os.getenv('okx_api_key')
okx_api_secret = os.getenv('okx_api_secret')
okx_api_passphrase = os.getenv('okx_api_passphrase')
okx_url_trade = os.getenv('okx_url_trade')

tg_session_name = os.getenv('tg_session_name')
tg_signal_channel_id = int(os.getenv('tg_signal_channel_id'))
tg_log_channel_id = int(os.getenv('tg_log_channel_id'))

enable_trading = os.getenv('enable_trading') == 'True'
limit_funds = float(os.getenv('limit_funds'))
activity_level = float(os.getenv('activity_level'))
limit_count_trades = int(os.getenv('limit_count_trades'))
fee = float(os.getenv('fee'))

buy_half_level = float(os.getenv('buy_half_level'))
close_high_level = float(os.getenv('close_high_level'))


first_loss_zone = float(os.getenv('first_loss_zone'))
second_loss_zone = float(os.getenv('second_loss_zone'))
critical_loss_zone = float(os.getenv('critical_loss_zone'))

first_loss_time = int(os.getenv('first_loss_time'))
second_loss_time = int(os.getenv('second_loss_time'))
critical_loss_time = int(os.getenv('critical_loss_time'))