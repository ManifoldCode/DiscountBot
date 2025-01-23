from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", hide_input_in_errors=True)

    BOT_TOKEN: str
    CHANNEL_ID: str
    ADMIN_ID: int


config = Config()  # pyright: ignore[reportCallIssue]
