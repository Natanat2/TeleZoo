import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# Токен вашего бота
TOKEN = '7408912366:AAGb0eztKX1Ez-BWZ-cm751SclPgKZpn6Go'

# Создаем экземпляры бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Вопросы для викторины
quiz_data = [
    {
        "question": "Где вы хотели бы жить?",
        "options": ["В густом лесу", "На жарком побережье", "В заснеженных горах", "В городской суете"],
        "mapping": {
            "В густом лесу": "Лев",
            "На жарком побережье": "Фламинго",
            "В заснеженных горах": "Белый медведь",
            "В городской суете": "Крыса"
        }
    },
    # Другие вопросы
]

# Словарь для хранения состояния пользователей
user_states = {}

# Обработчик команды /start
@dp.message(Command('start'))
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text = "Начать викторину 🧠", callback_data = "start_quiz")],
        [InlineKeyboardButton(text = "О зоопарке 🐾", callback_data = "about_zoo")],
    ])
    await message.answer(
        "Привет! Это телеграм Московского Зоопарка. 🐾 Выберите действие:",
        reply_markup = keyboard
    )


# Обработчик кнопки "О зоопарке"
@dp.callback_query(lambda c: c.data == "about_zoo")
async def about_zoo(callback: CallbackQuery):
    text = "Московский зоопарк..."
    await callback.message.answer(text)
    await callback.answer()


# Обработчик кнопки "Начать викторину"
@dp.callback_query(lambda c: c.data == "start_quiz")
async def start_quiz(callback: CallbackQuery):
    user_states[callback.from_user.id] = {"current_question": 0, "answers": []}
    await send_question(callback.from_user.id)


# Функция для отправки следующего вопроса
async def send_question(user_id):
    state = user_states[user_id]
    question_data = quiz_data[state["current_question"]]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard = [
            [InlineKeyboardButton(text = option, callback_data = f"quiz_option:{option}")]
            for option in question_data["options"]
        ]
    )
    await bot.send_message(
        chat_id = user_id,
        text = f"Вопрос {state['current_question'] + 1}: {question_data['question']}",
        reply_markup = keyboard
    )


# Обработчик ответа на вопрос
@dp.callback_query(lambda c: c.data.startswith("quiz_option:"))
async def handle_quiz_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = user_states[user_id]
    question_data = quiz_data[state["current_question"]]
    selected_option = callback.data.split(":")[1]

    # Сохраняем ответ
    state["answers"].append(selected_option)

    # Переходим к следующему вопросу или завершаем викторину
    state["current_question"] += 1
    if state["current_question"] < len(quiz_data):
        await send_question(user_id)
    else:
        # Определяем тотемное животное
        animal_scores = {}
        for i, answer in enumerate(state["answers"]):
            mapping = quiz_data[i]["mapping"]
            animal = mapping[answer]
            animal_scores[animal] = animal_scores.get(animal, 0) + 1

        total_animal = max(animal_scores, key = animal_scores.get)

        animal_images = {
            "Лев": "https://storage.moscowzoo.ru/storage/647edc2a70bb5462366280fc/images/animals/fc387a69-37f8-4bbb-af2e-432a1a7a1640.jpeg",
            # Другие изображения
        }

        await callback.message.answer(f"Ваш тотем: {total_animal} 🐾")
        await bot.send_photo(
            chat_id = user_id,
            photo = animal_images[total_animal],
            caption = f"Поздравляю! {total_animal} — ваше тотемное животное!"
        )

        del user_states[user_id]  # Удаляем состояние пользователя

    await callback.answer()


# Основная функция для запуска бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
