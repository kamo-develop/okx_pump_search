from candles_manager import CandlesManager


class Order:

    def __init__(self, price, quantity, side, time, ):
        self.price = price
        self.quantity = quantity
        self.side = side
        self.time = time


class CorrectionHunter:

    def __init__(self, instrument_name, last_price):
        self.instrument_name = instrument_name
        self.last_price = last_price
        self.orders = list()

    # async def run(self):
    #     while True:
    #         pass

    # Принятие решений на основне изменения цены
    async def on_price_update(self, candles_manager: CandlesManager):
        pass

    async def place_buy_order(self):
        order_price = 0
        order_quantity = 0

