from pprint import pprint
from typing import List, Dict

from okx.websocket.WsPublic import WsPublic

def _callback(message):
    # arg = message.get("arg")
    print('_callback')
    pprint(message)
    # if not arg or not arg.get("channel"):
    #     return
    # if message.get("event") == "subscribe":
    #     return
    # if arg.get("channel") in ["books5", "books", "bbo-tbt", "books50-l2-tbt", "books-l2-tbt"]:
    #     pass

class WssMarketDataService(WsPublic):
    def __init__(self, url, inst_id, channel):
        super().__init__(url)
        self.inst_id = inst_id
        self.channel = channel
        self.args = []

    def run_service(self):
        args = self._prepare_args()
        print(args)
        print("subscribing")
        self.subscribe(args, _callback)
        self.args += args

    def stop_service(self):
        self.unsubscribe(self.args, lambda message: print(message))
        self.close()

    def _prepare_args(self) -> List[Dict]:
        args = []
        subscribe_data = {
            "channel": self.channel,
            "instId": self.inst_id
        }
        args.append(subscribe_data)
        return args