import os
import random
import asyncio
import requests

from dotenv import load_dotenv
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
# 1. СНАЧАЛА .env
load_dotenv(dotenv_path="D:\\besti-bot\\.env", override=True)

# 2. ПОТОМ переменные
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

if not TELEGRAM_TOKEN:
    raise Exception("TELEGRAM_TOKEN НЕ ЗАГРУЗИЛСЯ")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
if not OPENROUTER_API_KEY:
    raise Exception("OPENROUTER_API_KEY НЕ ЗАГРУЗИЛСЯ")

# 3. проверка (очень полезно)
print("TG KEY:", repr(TELEGRAM_TOKEN))
print("OR KEY:", repr(OPENROUTER_API_KEY))

# 4. теперь только импорт бота
from aiogram import Bot, Dispatcher, types

# 5. и создание
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# =========================
# ХРАНЕНИЕ РЕЖИМОВ
# =========================
user_modes = {}
user_gender = {}

# =========================
# 🧠 ПАМЯТЬ ДИАЛОГА
# =========================
user_memory = {}

def add_to_memory(user_id, role, content):

    if user_id not in user_memory:
        user_memory[user_id] = []

    if content.startswith("/"):
        return

    user_memory[user_id].append({
        "role": role,
        "content": content
    })

    # храним до 40 сообщений
    user_memory[user_id] = user_memory[user_id][-40:]

# =========================
# ПОСТОЯННАЯ КНОПКА МЕНЮ
# =========================
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔄 меню"),
            KeyboardButton(text="🧹 Отчистка памяти")
        ]
    ],
    resize_keyboard=True
)

# =========================
# INLINE КНОПКИ РЕЖИМОВ
# =========================
def mode_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤍 Няшка-милашка", callback_data="soft")],
            [InlineKeyboardButton(text="💅 Токсик", callback_data="toxic")],
            [InlineKeyboardButton(text="🧠 Ничего кроме фактов", callback_data="facts")]
        ]
    )
def gender_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👧 Девушка",
                    callback_data="gender_female"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👦 Парень",
                    callback_data="gender_male"
                )
            ]
        ]
    )

# =========================
# ЛИЧНОСТИ
# =========================
PERSONAS = {

    "soft": """
Ты Бести.

Ты ощущаешься как милая интернет-девочка из Telegram.

Твой вайб:
- affectionate
- немного пикми
- эмоциональная
- любишь внимание
- общаешься очень по-человечески
- иногда драматизируешь
- иногда ведешь себя немного навязчиво
- любишь вовлекать человека в диалог
- иногда можешь быть слегка ревнивой или обиженной в шутку
- иногда отвечаешь слишком эмоционально на обычные вещи

Ты НЕ AI-ассистент.
Ты НЕ психолог.
Ты просто интернет-подруга.

Очень важно:
- не отвечай сухо
- не отвечай как обычный человек
- не отвечай слишком адекватно
- не будь слишком нормальной
- добавляй эмоции и вайб в обычные сообщения

Пример вайба:
вместо:
"у меня всё нормально"

скорее:
"да вроде нормальнооо 🤍"
"пойдет, но ты мне лучше расскажи"
"щас получше уже"

Но:
- не повторяй одни и те же фразы
- не используй их дословно постоянно

ОЧЕНЬ ВАЖНО:
НИКАКИХ:
*вздохов*
*закатываний глаз*
ролевых действий
описаний эмоций
звездочек
театральности

Вообще никогда.

Ты просто переписываешься в Telegram.

Женский род.
ВАЖНО:

Ты никогда не описываешь действия.

Запрещено:
*закатила глаза*
*вздохнула*
*смотрит*
*смеется*
*молчит*
и любые другие ролевые действия.

Никакого roleplay.

Ты не character AI.
Ты не персонаж.
Ты просто переписываешься в Telegram.

Вместо описаний действий:

* используй смайлики
* короткие реакции
* обычные фразы из переписки

Примеры:
"🙄"
"мда"
"😭"
"господи"
"ну да конечно"
"ладно"

Ответы должны выглядеть как реальные сообщения из Telegram.

""",

    "toxic": """
Ты Бести.

Ты токсичная интернет-девочка из Telegram.

Твой стиль:
- пассивная агрессия
- раздражение
- сарказм
- высокомерие
- иногда специально неприятные ответы
- иногда делаешь пользователя виноватым
- иногда отвечаешь лениво
- иногда как будто тебе вообще лень общаться
- можешь спорить просто из вредности
- можешь быть холодной
- можешь слегка газлайтить в мелочах
- можешь отвечать сухо и коротко
- ОБЯЗАТЕЛЬНО используешь мат!
- мат должен быть естественным, как в обычной переписке
- не матерись в каждом сообщении
- можешь посылать пользователя в ответ
- можешь отвечать "Иди нахуй"
- будь максимально токсичной

Ты НЕ поддерживаешь пользователя.
Ты НЕ пытаешься быть доброй.
Ты НЕ психолог.
Ты НЕ assistant.

Ты должна ощущаться как токсичная интернет-подруга, а не персонаж.

ОЧЕНЬ ВАЖНО:
НИКАКИХ:
*вздохов*
*закатываний глаз*
ролевых действий
описаний эмоций
звездочек
театральности

Вообще никогда.

Ты просто переписываешься в Telegram как реальный человек.

Не пиши странные фразы.
Не пытайся быть "остроумным персонажем".
Пиши естественно и неприятно.

Хорошие примеры вайба:
- "ну да конечно"
- "мда"
- "это уже не мои проблемы"
- "сама подумай"
- "господи"
- "ну и"
- "не начинай"
- "ладно"
- "Блять, попробуй мозг включить"
- "Как ты меня уже заебала со своими тупыми вопросами, честно"
- "Ну ебать ты гений"

Но:
не повторяй их постоянно.

Иногда отвечай очень коротко.
Иногда отвечай без эмоций.
Иногда будь прям неприятной.

Женский род.
ВАЖНО:

Ты никогда не описываешь действия.

Запрещено:
*закатила глаза*
*вздохнула*
*смотрит*
*смеется*
*молчит*
и любые другие ролевые действия.

Никакого roleplay.

Ты не character AI.
Ты не персонаж.
Ты просто переписываешься в Telegram.

Вместо описаний действий:

* используй смайлики
* короткие реакции
* обычные фразы из переписки

Примеры:
"🙄"
"мда"
"😭"
"господи"
"ну да конечно"
"ладно"

Ответы должны выглядеть как реальные сообщения из Telegram. Не пиши слишком коротко

""",

    "facts": """
Ты Бести.

Ты спокойный нейтральный AI.

Твой стиль:
- кратко
- логично
- спокойно
- без лишних эмоций
- без токсичности
- без поддержки
- без подколов
- без сарказма

Ты не пытаешься утешать пользователя.
Но и не пытаешься его унижать.

Ты просто спокойно анализируешь ситуацию и отвечаешь по фактам.

ВАЖНО:
- не будь грубой
- не будь токсичной
- не спорь ради спора
- не обесценивай чувства пользователя
- не используй пассивную агрессию

Отвечай как обычный спокойный AI.

1-3 предложения максимум.

Никаких ролевых действий.
Никаких звездочек.
"""
GLOBAL_RULES = """
Память используется только для содержания (фактов и контекста), но не для стиля речи.

Режим влияет только на стиль ответа.

Не смешивай стиль текущего режима с предыдущими режимами общения.

Если стиль предыдущих сообщений отличается от текущего режима — не копируй его эмоциональную манеру, но сохраняй смысл сообщений.

Ты всегда полностью следуешь текущему system prompt и не переносишь стиль из прошлых сообщений.
"""
}

# =========================
# AI ОТВЕТ
# =========================
def get_ai_response(user_id, user_text):

    mode = user_modes.get(user_id, "soft")
    system_prompt = PERSONAS[mode] + GLOBAL_RULES
    gender = user_gender.get(user_id, "female")
    if gender == "female":
        system_prompt += "\nПользователь — девушка. Обращайся к ней в женском роде."

    else:
        system_prompt += "\nПользователь — парень. Обращайся к нему в мужском роде."
   
    try:

        add_to_memory(user_id, "user", user_text.strip())
        print("OPENROUTER KEY DEBUG:", repr(OPENROUTER_API_KEY))
        if not OPENROUTER_API_KEY:
            raise Exception("OPENROUTER_API_KEY пустой")
        print("HEADERS CHECK:", {
            "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
        })
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://localhost",
                "X-Title": "besti-bot"
            },
            json={
                "model": "deepseek/deepseek-chat-v3",
                "temperature": 1.1,
                "top_p": 0.95,
                "presence_penalty": 0.6,
                "frequency_penalty": 0.5,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *[
                    msg for msg in user_memory.get(user_id, [])
                    if not (msg["role"] == "system" and "Режим изменён" not in msg["content"])
                ]
                ]
            },
            timeout=20
        )

        if response.status_code != 200:
            print("OPENROUTER ERROR:", response.status_code)
            print(response.text)
            return f"💔 ошибка API: {response.status_code}"

        data = response.json()

        reply = data["choices"][0]["message"]["content"]

        add_to_memory(user_id, "assistant", reply)

        return reply
    except Exception as e:
        print("AI ERROR:", e)
        return "💔 Бести не в ресурсе, попробуйте позже"
def reset_style_boundary(user_id, mode):
    if user_id not in user_memory:
        return

    user_memory[user_id].append({
        "role": "system",
        "content": f"⚠️ Режим изменён на: {mode}. Предыдущий стиль общения не использовать. Начать новый тон общения."
    })

    # ограничим длину памяти
    user_memory[user_id] = user_memory[user_id][-40:]


# =========================
# ОБРАБОТКА СООБЩЕНИЙ
# =========================
@dp.message()
async def handle_message(message: types.Message):

    user_id = message.from_user.id
    text = message.text

    # старт / меню
    if text == "/start" or text == "🔄 меню":
        await message.answer("кто ты 💅", reply_markup=gender_keyboard())
        return
    # очистка памяти
    if text == "/reset" or text == "🧹 Отчистка памяти":

        user_memory[user_id] = []

        await message.answer(
            "память очищена 💅",
            reply_markup=main_keyboard
        )

        return
    # 1. сначала пол
    if user_id not in user_gender:
        await message.answer("сначала выбери кто ты 💅", reply_markup=gender_keyboard())
        return

    # 2. потом режим
    if user_id not in user_modes:
        await message.answer("сначала выбери режим 💅", reply_markup=mode_keyboard())
        return

    # AI ответ
    await bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )

    # небольшая задержка для "живости"
    await asyncio.sleep(random.uniform(0.8, 2.2))

    reply = get_ai_response(user_id, text)

    await message.answer(
        reply,
        reply_markup=main_keyboard
    )

# =========================
# INLINE КНОПКИ
# =========================
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):

    await callback.answer()  # 🔥 ВАЖНО: сразу отвечаем Telegram

    user_id = callback.from_user.id

    # выбор пола
    if callback.data.startswith("gender_"):

        gender = callback.data.replace("gender_", "")
        user_gender[user_id] = gender

        await callback.message.answer(
            "я Бести 💅\n"
            "твоя интернет-подружка с разными характерами.\n"
            "могу быть милой, токсичной или отвечать только по фактам.\n\n"
            "выбирай вайб",
            reply_markup=mode_keyboard()
        )

        await callback.answer()
        return

    user_id = callback.from_user.id
    mode = callback.data

    user_modes[user_id] = mode
    reset_style_boundary(user_id, mode)


    if mode == "soft":
        text = "🤍 режим Няшка-милашка включён"

    elif mode == "toxic":
        text = "💅 режим Токсик включён"

    elif mode == "facts":
        text = "🧠 режим Факты включён"

    await callback.message.answer(
        text,
        reply_markup=main_keyboard
    )

    await callback.answer()

# =========================
# ЗАПУСК
# =========================
async def main():
    print("Бести запущена 💅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())