from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='services/trades/settings.env',
        env_file_encoding='utf-8'
    )

    symbols: list[str] = [
        'BTC/USD',
        'BTC/EUR',
        'ETH/EUR',
        'ETH/USD',
        'SOL/USD',
        'SOL/EUR',
        'XRP/USD',
        'XRP/EUR',        
    ]

    kafka_broker_address: str
    kafka_topic_name: str

config = Settings()

