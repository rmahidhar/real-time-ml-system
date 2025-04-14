from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='services/candles/settings.env', env_file_encoding='utf-8'
    )

    kafka_broker_address: str
    kafka_trades_topic: str
    kafka_candles_topic: str
    kafka_consumer_group: str
    candle_seconds: int


config = Settings()
