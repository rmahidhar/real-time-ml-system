from loguru import logger
from quixstreams import Application


def init_candle(trade: dict) -> dict:
    """
    Initialize a candle with the first trade
    Return the initial candle state

    Args:
        trade (dict): The first trade

    Returns:
        dict: The initial candle state
    """
    return {
        'open': trade['price'],
        'high': trade['price'],
        'low': trade['price'],
        'close': trade['price'],
        'volume': trade['quantity'],
        'symbol': trade['symbol'],
    }


def update_candle(candle: dict, trade: dict) -> dict:
    """
    Takes the current candle (aka state) and the new trade, and updates
    the candle state

    Args:
        candle (dict): The current candle state
        trade (dict): The new trade

    Returns:
        dict: The updated candle state
    """
    # open price does not change, so there is no need to update it
    candle['high'] = max(candle['high'], trade['price'])
    candle['low'] = min(candle['low'], trade['price'])
    candle['close'] = trade['price']
    candle['volume'] += trade['quantity']

    return candle


def run(
    kafka_broker_address: str,
    kafka_trades_topic: str,
    kafka_candles_topic: str,
    kafka_consumer_group: str,
    candle_seconds: int,
    emit_intermediate_candles: bool = True,
):
    """
    Transforms a stream of input trades into a stream of output candles.

    In 3 steps:
        - Ingests trade from the kafka_trades_topic
        - Aggregates trades into candles
        - Produces candles to the kafka_candles_topic

    Args:
        kafka_broker_address (str): Kafka broker address
        kafka_trades_topic (str): Kafka input topic name
        kafka_candles_topic (str): Kafka output topic name
        kafka_consumer_group (str): Kafka consumer group name
        candle_seconds (int): Candle duration in seconds

    Returns:
        None
    """

    app = Application(
        broker_address=kafka_broker_address, consumer_group=kafka_consumer_group
    )

    # input topic
    trades_topic = app.topic(kafka_trades_topic, value_deserializer='json')

    # output topic
    candles_topic = app.topic(kafka_candles_topic, value_serializer='json')

    # step 1. ingest trades from trades topic
    # create a streaming dataframe connected to the trades topic
    sdf = app.dataframe(topic=trades_topic)

    # step 2. aggregate trades into candles
    # TODO: at the moment I am just printing it, to make sure this thing works.
    # sdf = sdf.update(lambda message: logger.info(f'Input:  {message}'))
    from datetime import timedelta

    sdf = (
        # define a tumbling window of 10 minutes
        sdf.tumbling_window(timedelta(seconds=candle_seconds))
        # create a "reduce" aggregation with "reducer" and "initializer" functions
        .reduce(reducer=update_candle, initializer=init_candle)
    )

    # we emit all intermeidate candles to make the system more responsive
    sdf = sdf.current()

    sdf['open'] = sdf['value']['open']
    sdf['high'] = sdf['value']['high']
    sdf['low'] = sdf['value']['low']
    sdf['close'] = sdf['value']['close']
    sdf['volume'] = sdf['value']['volume']
    # sdf['timestamp_ms'] = sdf['value']['timestamp_ms']
    sdf['symbol'] = sdf['value']['symbol']

    # extract window start and end timestamps
    sdf['window_start_ms'] = sdf['start']
    sdf['window_end_ms'] = sdf['end']

    # keep only the relevant columns
    sdf = sdf[
        [
            'symbol',
            # "timestamp_ms",
            'open',
            'high',
            'low',
            'close',
            'volume',
            'window_start_ms',
            'window_end_ms',
        ]
    ]

    sdf['candle_seconds'] = candle_seconds

    # logging on the console
    sdf = sdf.update(lambda value: logger.debug(f'candle: {value}'))

    # step 3. produce the candles to the candles topic
    sdf = sdf.to_topic(candles_topic)

    # starts the streaming app
    app.run()


if __name__ == '__main__':
    from candles.config import config

    run(
        kafka_broker_address=config.kafka_broker_address,
        kafka_trades_topic=config.kafka_trades_topic,
        kafka_candles_topic=config.kafka_candles_topic,
        kafka_consumer_group=config.kafka_consumer_group,
        candle_seconds=config.candle_seconds,
    )
