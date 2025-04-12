
from trades.kraken_api import KrakenAPI, Trade
from loguru import logger
from quixstreams import Application

def run(
        kafka_broker_address: str,
        kafka_topic_name: str,
        kraken_api: KrakenAPI,
):
    # create a Quix application
    app = Application(kafka_broker_address)

    # define a topic "my_topic" with JSON serialization
    topic = app.topic(name=kafka_topic_name, value_serializer='json')

    # create a producer instance
    with app.get_producer() as producer:
        while True:
            # 1. Fetch the event from the external API
            events: list[Trade] = kraken_api.get_trades()

            for event in events:
                # 2. serialize an event using the defined topic
                message = topic.serialize(key=event.symbol, value=event.to_dict())

                # 3. produce a message into the kafka topic
                producer.produce(topic=topic.name, value=message.value, key=message.key)

                logger.info(f"Produced a message to the topic {topic.name}")


if __name__ == "__main__":
    from trades.config import config

    # create object that can talk to the Kraken API and get us the trade
    # data in real time
    api = KrakenAPI(symbols=config.symbols)

    run(
        kafka_broker_address=config.kafka_broker_address,
        kafka_topic_name=config.kafka_topic_name,
        kraken_api=api,
    )

