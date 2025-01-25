import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command

# Токен вашего бота
TOKEN = '7408912366:AAGb0eztKX1Ez-BWZ-cm751SclPgKZpn6Go'

# Создаем экземпляры бота и диспетчера
bot = Bot(token = TOKEN)
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
    {
        "question": "Какую еду вы предпочитаете?",
        "options": ["Мясо", "Овощи", "Рыба", "Сладости"],
        "mapping": {
            "Мясо": "Лев",
            "Овощи": "Рысь",
            "Рыба": "Фламинго",
            "Сладости": "Крыса"
        }
    },
    {
        "question": "Какой ваш любимый цвет?",
        "options": ["Красный", "Синий", "Зеленый", "Желтый"],
        "mapping": {
            "Красный": "Лев",
            "Синий": "Белый медведь",
            "Зеленый": "Лев",
            "Желтый": "Фламинго"
        }
    },
    {
        "question": "Какой ваш любимый стиль жизни?",
        "options": ["Активный", "Спокойный", "Природный", "Городской"],
        "mapping": {
            "Активный": "Лев",
            "Спокойный": "Рысь",
            "Природный": "Фламинго",
            "Городской": "Крыса"
        }
    },
    {
        "question": "Как вы относитесь к одиночеству?",
        "options": ["Люблю одиночество", "Не могу без компании", "Мне все равно", "Зависит от ситуации"],
        "mapping": {
            "Люблю одиночество": "Белый медведь",
            "Не могу без компании": "Крыса",
            "Мне все равно": "Лев",
            "Зависит от ситуации": "Фламинго"
        }
    },
]

# Словарь для хранения состояния пользователей
user_states = {}

logo = FSInputFile('media/logo.jpg')


# Обработчик команды /start
@dp.message(Command('start'))
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text = "Начать викторину 🧠", callback_data = "start_quiz")],
        [InlineKeyboardButton(text = "О зоопарке 🐾", callback_data = "about_zoo")],
    ])

    # Отправляем логотип
    await bot.send_photo(
        chat_id = message.chat.id,
        photo = logo,
        caption = "Добро пожаловать в Московский зоопарк! Это телеграм Московского Зоопарка. 🐾 Выберите действие:",
        reply_markup = keyboard
    )


# Обработчик кнопки "О зоопарке"
@dp.callback_query(lambda c: c.data == "about_zoo")
async def about_zoo(callback: CallbackQuery):
    text = (
        "Московский зоопарк — один из старейших зоопарков Европы. Он был открыт 31 января 1864 года по старому стилю и назывался тогда зоосадом.\n\n"
        "Московский зоопарк был организован Императорским русским обществом акклиматизации животных и растений.\n\n"
        "Начало его существования связано с замечательными именами профессоров Московского Университета Карла Францевича Рулье, Анатолия Петровича Богданова и Сергея Алексеевича Усова.\n\n"
        "Местность, где теперь находится Старая территория зоопарка, называлась «Пресненские пруды». Здесь протекала довольно широкая река Пресня, и было одно из любимых мест гуляний москвичей — зелёные холмы, заливные луга, цветущие сады украшали окрестности.\n\n"
        "Для создания зоосада большинством голосов членов Общества акклиматизации был выбран именно этот участок, так как он находился на доступном расстоянии для всех москвичей, в том числе и небогатых. Территория Петровской академии, например, была удобнее и больше, но ездить туда было бы далеко и дорого для большинства потенциальных посетителей.\n\n"
        "Подробнее: [Московский зоопарк](https://moscowzoo.ru/about)"
    )
    await callback.message.answer(text, disable_web_page_preview = True)
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
        # Подсчитываем ответы и определяем тотемное животное
        animal_scores = {}
        for i, answer in enumerate(state["answers"]):
            mapping = quiz_data[i]["mapping"]
            animal = mapping[answer]
            animal_scores[animal] = animal_scores.get(animal, 0) + 1

        total_animal = max(animal_scores, key = animal_scores.get)

        animal_images = {
            "Лев": "media/lion.png",
            "Фламинго": "media/flamingo.png",
            "Белый медведь": "media/bear.png",
            "Рысь": "media/Ris.png",
            "Крыса": "media/rat.png",
        }

        await bot.send_photo(
            chat_id = user_id,
            photo = FSInputFile(animal_images[total_animal]),
            caption = f"Поздравляю! {total_animal} — ваше тотемное животное!"
        )

        # Удаляем состояние пользователя после завершения викторины
        del user_states[user_id]

    await callback.answer()


# Основная функция для запуска бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
