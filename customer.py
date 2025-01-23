from sqlmodel import Field, SQLModel


class Customer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True)
    promo_code: int = Field(index=True, unique=True)
    has_used_discount: bool = Field(default=False)
    subscribed: bool = Field(default=False)
