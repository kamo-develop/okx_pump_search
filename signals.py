import time

from tg_manager import TelegramManager


class Pump:

    def __init__(self, pump_force, average_force, count_force, pump_time):
        self.time = pump_time
        self.pump_force = pump_force
        self.average_force = average_force
        self.count_forces = count_force


class SignalManager:

    def __init__(self, tg_manager: TelegramManager, margin_instruments: set):
        self.pumps = dict()
        self.pump_duration = 300
        self.tg_manager = tg_manager
        self.margin_instruments = margin_instruments

    def new_pump(self, instrument_name, pump_force, average_force, count_forces):
        if instrument_name not in self.pumps:
            self.pumps[instrument_name] = Pump(pump_force, average_force, count_forces, int(time.time()))
            self.tg_manager.on_new_pump(instrument_name, pump_force, average_force, count_forces, instrument_name in self.margin_instruments)
        else:
            self.pumps[instrument_name] = Pump(pump_force, average_force, count_forces, self.pumps[instrument_name].time)
            if int(time.time()) - self.pumps[instrument_name].time > self.pump_duration:
                self.pumps[instrument_name].time = int(time.time())
                self.tg_manager.on_new_pump(instrument_name, pump_force, average_force, count_forces, instrument_name in self.margin_instruments)
            else:
                pass




