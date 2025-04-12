import json

from loguru import logger
from pydantic import BaseModel
from websocket import create_connection

class Trade(BaseModel):
    symbol: str
    price: float
    quantity: float
    timestamp: str

    def to_dict(self) -> dict:
        return self.model_dump()

class KrakenAPI:
    URL = "wss://ws.kraken.com/v2"

    def __init__(self, symbols: list[str]):
        self.symbols = symbols

        # create a websocket connection
        self._ws_client = create_connection(self.URL)

        # send initial subscribe message
        self._subscribe(symbols)

    def get_trades(self) -> list[Trade]:
        data: str = self._ws_client.recv()

        if 'heartbeat' in data:
            logger.info("Heartbeat received")
            return []

        # transform raw string into a JSON object
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            return []

        try:
            trades_data = data['data']
        except KeyError:
            logger.error(f"No `data` field with trades in the message: {data}")
            return []

        return [
            Trade(
                symbol = trade['symbol'],
                price = trade['price'],
                quantity = trade['qty'],
                timestamp = trade['timestamp']
            )
            for trade in trades_data
        ]

    def _subscribe(self, symbols: list[str]):
        # send a subscribe message to the websocket
        self._ws_client.send(
            json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": "trade",
                    "symbol": symbols,
                    "snapshot": False
                },
            })
        )

        # discard the first 2 messages for each symbol as
        # they contain no trade data
        for _ in symbols:
            self._ws_client.recv()
            self._ws_client.recv()

