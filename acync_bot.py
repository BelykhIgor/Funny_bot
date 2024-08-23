import random
import logging
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv
from config import BOT_TOKEN
from gigachat_request import post_request_gigachat, post_request_gigachat_media

load_dotenv()

# Ваш токен, который вы получили от BotFather
TOKEN = BOT_TOKEN

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
dp = Dispatcher()
bot = Bot(token=TOKEN)

user_states = {}

# Установка команд для штатного меню
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/about", description="О боте"),
        BotCommand(command="/contact", description="Контакты")
    ]
    await bot.set_my_commands(commands)

# Обработчик команды /start
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    logger.info("Start item Start")
    user = message.from_user
    logger.info(
        f"User: "
        f"user_name: {user.username} "
        f"| user_id: {user.id} "
        f"| first_name: {user.first_name} "
        f"| last_name: {user.last_name} "
        f"| language_code: {user.language_code}"
    )

    markup_main = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Факт", callback_data="fact"),
         InlineKeyboardButton(text="Поговорка", callback_data="think")],
        [InlineKeyboardButton(text="Анекдот", callback_data="joke"),
         InlineKeyboardButton(text="Притчи", callback_data="parable")],
        [InlineKeyboardButton(text="GigaChat", callback_data="gigachat"),
         InlineKeyboardButton(text="Тосты", callback_data="toasts")],
        [
            InlineKeyboardButton(text="GigaChatMedia", callback_data="gigachat_media"),
        ]
    ])

    await message.answer(
        '*Нажми*: \n*Факт* — для получения интересного факта'
        '\n*Поговорка* — для получения мудрой цитаты'
        '\n*Анекдот* — для получения анекдота'
        '\n*Притчи* — для получения притчи'
        '\n*GigaChat* — задай свой вопрос нейросети'
        '\n*Тосты* — праздничные тосты'
        '\n*GigaChatMedia* — Может нарисовать картину по запросу',
        reply_markup=markup_main,
        parse_mode='Markdown',
    )

# Обработчик команды /help
@dp.message(Command("help"))
async def send_help(message: types.Message):
    logger.info("Start item Help")
    await message.answer(
        "Я могу отвечать на ваши сообщения. Просто напишите что-нибудь!",
        parse_mode='Markdown'
    )

# Обработчик команды /about
@dp.message(Command("about"))
async def send_about(message: types.Message):
    logger.info("Start item About")
    await message.answer(
        "Этот бот умеет общаться с людьми и может рассказать им много интересного.\n"
        "*Он знает огромное количество фактов обо всём на свете, а также любит делиться* "
        "_народной мудростью_. Если вам скучно или хочется узнать что-то новое, этот бот "
        "*всегда готов составить вам компанию.*",
        parse_mode='Markdown'
    )

# Обработчик команды /contact
@dp.message(Command("contact"))
async def send_contact(message: types.Message):
    logger.info("Start item Contact")
    await message.answer(
        "Свяжитесь с нами по адресу: contact@example.com",
        parse_mode='Markdown'
    )

# Загружаем списки
with open('load_data/facts.txt', 'r', encoding='UTF-8') as f:
    facts = f.read().split('\n')

with open('load_data/thinks.txt', 'r', encoding='UTF-8') as f:
    thinks = f.read().split('\n')

with open('load_data/jokes.txt', 'r', encoding='UTF-8') as f:
    joke = f.read().split('* * *')

with open('load_data/parables.txt', 'r', encoding='UTF-8') as f:
    parable = f.read().split('* * *')

with open("load_data/toasts.txt", "r", encoding="UTF-8") as f:
    toasts = f.read().split("*****")

# Функция для экранирования специальных символов в Markdown
def escape_markdown(text):
    escape_chars = r'\*_`['
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# Обработчик нажатий на кнопки
@dp.callback_query(lambda call: True)
async def callback_query(call: types.CallbackQuery):
    logger.info(f"Start callback_query - {call.data}")
    try:
        user_id = call.from_user.id
        if call.data == "fact":
            answer = random.choice(facts)
            await call.message.answer(f'`{escape_markdown(answer)}`', parse_mode='Markdown')
        elif call.data == "think":
            answer = random.choice(thinks)
            await call.message.answer(f'`{escape_markdown(answer)}`', parse_mode='Markdown')
        elif call.data == "joke":
            answer = random.choice(joke)
            await call.message.answer(f'`{escape_markdown(answer)}`', parse_mode='Markdown')
        elif call.data == "parable":
            answer = random.choice(parable)
            await call.message.answer(f'`{escape_markdown(answer)}`', parse_mode='Markdown')
        elif call.data == "gigachat":
            await call.message.answer('Задай свой вопрос нейросети:', parse_mode='Markdown')
            user_states[user_id] = "gigachat"
            return
        elif call.data == "gigachat_media":
            await call.message.answer(
                'Что будем рисовать? \n\n_Запрос должен начинаться со слова нарисуй или же промт_',
                parse_mode='Markdown'
            )
            user_states[user_id] = "gigachat_media"
            return
        elif call.data == "toasts":
            answer = random.choice(toasts)
            await call.message.answer(f'`{escape_markdown(answer)}`', parse_mode='Markdown')
        elif call.data == "again":
            await call.message.answer("Попробуйте ещё раз.")
        elif call.data == "main_menu":
            await send_welcome(call.message)
            return

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ещё раз", callback_data=call.data),
             InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
        ])
        await call.message.answer("Выберите действие:", reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in callback_query: {e}")

# Получение сообщений от юзера
@dp.message()
async def handle_text(message):
    logger.info("Start handle_text")
    user_id = message.from_user.id

    try:
        if user_id in user_states:
            state = user_states[user_id]
            if state == "gigachat":
                await bot.send_message(message.chat.id, f'_Минуточку, идёт генерация ответа ..._', parse_mode='Markdown')
                request = await post_request_gigachat(message.text)
                await bot.send_message(message.chat.id, f"*Ответ нейросети:*\n{request}", parse_mode='Markdown')
                # Добавляем кнопки "Ещё раз" и "Главное меню"
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Задать еще вопрос", callback_data="gigachat"),
                     InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
                ])
                await bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
            elif state == "gigachat_media":
                await bot.send_message(message.chat.id, f'_Минуточку идёт генерация изображения ..._',
                                       parse_mode='Markdown')
                request = await post_request_gigachat_media(message.text)
                if "id_media" in request:
                    logger.info("Open media file")
                    await bot.send_message(message.chat.id, f"*Вот что получилось:*", parse_mode='Markdown')

                    file_path = f"images/{request["id_media"]}"
                    await bot.send_photo(message.chat.id, photo=types.FSInputFile(file_path))
                    # Добавляем кнопки "Ещё раз" и "Главное меню"
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Порисуем еще?", callback_data="gigachat_media"),
                         InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
                    ])
                    await bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
                elif "answer_text" in request:
                    await bot.send_message(
                        message.chat.id,
                        f"*Вот что получилось:*\n{request["answer_text"]}",
                        parse_mode='Markdown'
                    )
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Порисуем еще?", callback_data="gigachat_media"),
                         InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
                    ])
                    await bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
            del user_states[user_id]
        else:
            await bot.send_message(message.chat.id, "Пожалуйста, выберите действие из меню.")
    except Exception as e:
        logger.error(f"Error in handle_text: {e}")
        await bot.send_message(message.chat.id, "Произошла ошибка при обработке вашего запроса. Попробуйте еще раз.")



async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
