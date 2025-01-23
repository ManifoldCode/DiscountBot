import telebot
from config import config
from customer import Customer
from promo_code_generator import generate_promo_code
from sqlmodel import Session, SQLModel, create_engine, select
from telebot.types import CallbackQuery, Message
from value_utils import unwrap

bot = telebot.TeleBot(config.BOT_TOKEN)
engine = create_engine("sqlite:///database.db")


def add_user_to_db(user_id: int) -> None:
    with Session(engine) as session:
        user = session.exec(select(Customer).where(Customer.telegram_id == user_id)).first()
        if user is None:
            unique_key = generate_promo_code(session)
            new_user = Customer(telegram_id=user_id, promo_code=unique_key)
            session.add(new_user)
            session.commit()


@bot.message_handler(commands=["start"])
def send_welcome(message: Message) -> None:
    user_id = unwrap(message.from_user).id

    add_user_to_db(user_id)

    markup = telebot.types.InlineKeyboardMarkup()
    subscribe_button = telebot.types.InlineKeyboardButton(
        "Подписаться на канал", url=f"https://t.me/{config.CHANNEL_ID}"
    )
    check_button = telebot.types.InlineKeyboardButton(
        "Проверить подписку", callback_data="check_subscription"
    )
    _ = markup.add(subscribe_button, check_button)

    _ = bot.send_message(
        message.chat.id,
        "Чтобы получить скидку, подпишитесь на наш канал и нажмите 'Проверить подписку'.",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")  # pyright: ignore[reportUnknownLambdaType]
def check_customer_subscribed(call: CallbackQuery) -> None:
    _ = bot.answer_callback_query(call.id)
    user_id = call.from_user.id

    member_status = bot.get_chat_member(f"@{config.CHANNEL_ID}", user_id).status
    is_subscribed = member_status in ["member", "administrator", "creator"]

    with Session(engine) as session:
        user = session.exec(select(Customer).where(Customer.telegram_id == user_id)).first()
        if user is None:
            _ = bot.send_message(call.message.chat.id, "Вы не зарегистрированы. Введите /start.")
            return

        if is_subscribed:
            user.subscribed = True
            if not user.has_used_discount:
                _ = bot.send_message(
                    call.message.chat.id,
                    (
                        "Поздравляем! Вы получили скидку в размере 5%.\n"
                        f"Ваш код для применения скидки: {user.promo_code}."
                    ),
                )
            else:
                _ = bot.send_message(
                    call.message.chat.id,
                    ("Вы уже использовали скидку!\n" "Спасибо за то, что Вы с нами!"),
                )
            session.commit()
        else:
            _ = bot.send_message(
                call.message.chat.id,
                "Вы еще не подписались на канал. Пожалуйста, подпишитесь и попробуйте снова.",
            )


@bot.message_handler(commands=["sale"])
def check_promo_code(message: Message) -> None:
    user_id = unwrap(message.from_user).id
    chat_id = message.chat.id

    if user_id != config.ADMIN_ID:
        _ = bot.send_message(chat_id, "Вы не являетесь администратором.")
        return

    _ = bot.send_message(chat_id, "Введите промокод пользователя для проверки:")


@bot.message_handler(func=lambda message: message.text.isdigit())  # pyright: ignore[reportUnknownLambdaType]
def handle_promo_code(message: Message) -> None:
    promo_code = int(message.text)

    with Session(engine) as session:
        user = session.exec(select(Customer).where(Customer.promo_code == promo_code)).first()

        if user is None:
            _ = bot.send_message(
                message.chat.id,
                f"Пользователь с промокодом {promo_code} не найден. Проверьте введенные данные.",
            )
            return

        if user.has_used_discount:
            _ = bot.send_message(
                message.chat.id,
                f"Пользователь с промокодом {promo_code} уже использовал скидку.",
            )
        else:
            markup = telebot.types.InlineKeyboardMarkup()
            apply_discount_button = telebot.types.InlineKeyboardButton(
                "Применить скидку", callback_data=f"apply_discount_{user.telegram_id}"
            )
            _ = markup.add(apply_discount_button)
            _ = bot.send_message(
                message.chat.id,
                (
                    f"Пользователь с промокодом {promo_code} еще не использовал скидку 7%. "
                    "Нажмите кнопку ниже, чтобы применить скидку."
                ),
                reply_markup=markup,
            )


@bot.callback_query_handler(func=lambda call: call.data.startswith("apply_discount_"))  # pyright: ignore[reportUnknownLambdaType]
def apply_discount(call: CallbackQuery) -> None:
    user_id = int(call.data.split("_")[-1])

    with Session(engine) as session:
        user = session.exec(select(Customer).where(Customer.telegram_id == user_id)).first()

        if user is None:
            _ = bot.answer_callback_query(call.id, "Пользователь не найден.")
            _ = bot.send_message(call.message.chat.id, "Пользователь не найден.")
            return

        if not user.has_used_discount:
            user.has_used_discount = True
            session.add(user)
            session.commit()
            _ = bot.answer_callback_query(call.id, "Скидка успешно применена!")
            _ = bot.send_message(
                call.message.chat.id,
                f"Скидка для пользователя с ID {user_id} успешно применена.",
            )
        else:
            _ = bot.answer_callback_query(call.id, "Скидка уже была активирована ранее.")
            _ = bot.send_message(
                call.message.chat.id,
                f"Скидка для пользователя с ID {user_id} уже активирована ранее.",
            )


def main() -> None:
    SQLModel.metadata.create_all(engine)
    bot.polling()


if __name__ == "__main__":
    main()
