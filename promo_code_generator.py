import random

from sqlmodel import Session, select

from customer import Customer


def generate_promo_code(session: Session) -> int:
    while True:
        promo_code = random.randint(10000, 99999)  # noqa: S311
        customer = session.exec(select(Customer).where(Customer.promo_code == promo_code)).first()
        if customer is None:
            return promo_code
