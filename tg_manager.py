import asyncio

from pyrogram import Client, enums
from queue import Queue
from settings import tg_session_name, tg_signal_channel_id, okx_url_trade, tg_log_channel_id


class Messaege:
    def __init__(self, text, notification, chat_id):
        self.text = text
        self.notification = notification
        self.chat_id = chat_id

class TelegramManager:
    def __init__(self):
        self.messages = Queue()

    async def run(self):
        app = Client(tg_session_name)
        async with app:
            while True:
                if not self.messages.empty():
                    current_message: Messaege = self.messages.get()
                    await app.send_message(
                        current_message.chat_id,
                        current_message.text,
                        disable_web_page_preview=True,
                        parse_mode=enums.ParseMode.MARKDOWN,
                        disable_notification=not current_message.notification
                    )
                await asyncio.sleep(0.1)

    def on_start_up(self):
        self.messages.put(Messaege("I started the work", True, tg_log_channel_id))

    def on_shut_down(self):
        self.messages.put(Messaege("I went to SLEEP!", True, tg_log_channel_id))

    def on_new_pump(self, instrument_name, pump_force, average_force, count_forces, is_margin: bool):
        currency_name = instrument_name.split('-')[0]
        text = (f"❗️PUMP\n`{currency_name}`\n"
                f"{'🛑**MARGIN!**' if is_margin else 'SPOT'}\n\n"
                f"{okx_url_trade}/{instrument_name.lower()}\n"
                f"{round(pump_force, 2)}%\n"
                f"frequency = {count_forces}; average = {round(average_force, 2)}%")
        self.messages.put(Messaege(text, True, tg_signal_channel_id))

    def on_statistic(self, sorted_by_count):
        text = f"Statistic\n"
        count_items = min(len(sorted_by_count), 5)
        for i in range(count_items):
            instrument_name = sorted_by_count[i][0]
            currency_name = instrument_name.split('-')[0]
            value = sorted_by_count[i][1]
            text += f"`{currency_name}` : freq. = {value['count']}; avg. = {round(value['average'], 2)}%\n"
        self.messages.put(Messaege(text, False, tg_signal_channel_id))


# -1002090278893    Test
# -1002074047213    Pump Signals