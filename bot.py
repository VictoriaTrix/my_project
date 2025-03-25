import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from api import TOKEN
from city import get_cities, get_available_countries
from aiogram.client.default import DefaultBotProperties

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


available_countries = get_available_countries()
country_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=country)] for country in available_countries],
    resize_keyboard=True
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Новая игра"), KeyboardButton(text="Помощь")],
        [KeyboardButton(text="Стоп")]
    ],
    resize_keyboard=True
)

active_games = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Выбери страну для игры:", reply_markup=country_keyboard)

@dp.message(Command("newgame"))
async def new_game(message: types.Message):
    await start(message)

@dp.message(lambda message: message.text == "Новая игра")
async def new_game_button(message: types.Message):
    await start(message)

@dp.message(lambda message: message.text.strip() in available_countries)
async def select_country(message: types.Message):
    user_id = message.chat.id
    country = message.text.strip()

    cities = await get_cities(country) 

    if not cities:
        await message.answer(f" Не удалось загрузить города для {country}. Попробуйте позже.")
        return

    active_games[user_id] = {"cities": cities, "used_cities": set(), "last_letter": None}
    await message.answer(f"Страна выбрана: {country}. Напишите первый город!", reply_markup=main_keyboard)

@dp.message(Command("stop"))
async def stop_game(message: types.Message):
    user_id = message.chat.id
    if user_id in active_games:
        del active_games[user_id]
        await message.answer("Игра остановлена. Начните новую с командой /newgame.")
    else:
        await message.answer("Вы не начали игру. Используйте /newgame, чтобы начать.")

@dp.message(lambda message: message.text == "Стоп")
async def stop_game_button(message: types.Message):
    await stop_game(message)

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "/start – Выбрать страну для игры\n"
        "/newgame – Начать новую игру\n"
        "/stop – Завершить игру\n"
        "/help – Показать список команд"
    )

@dp.message(lambda message: message.text == "Помощь")
async def help_button(message: types.Message):
    await help_command(message)

@dp.message()
async def play_game(message: types.Message):
    user_id = message.chat.id
    city = message.text.strip().capitalize()

    if user_id not in active_games:
        await message.answer("Сначала выбери страну командой /start.")
        return

    game_data = active_games[user_id]

    if city in game_data["used_cities"]:
        await message.answer("Этот город уже был назван. Попробуйте другой.")
        return

    if city not in game_data["cities"]:
        await message.answer("Такого города нет в списке. Попробуйте снова.")
        return

    if game_data["last_letter"] and not city.lower().startswith(game_data["last_letter"]):
        await message.answer(f"Город должен начинаться с буквы {game_data['last_letter'].upper()}!")
        return

    game_data["used_cities"].add(city)
    last_letter = city[-1] if city[-1] not in "ьъы" else city[-2]
    game_data["last_letter"] = last_letter

    available_cities = [c for c in game_data["cities"] if c[0].lower() == last_letter and c not in game_data["used_cities"]]

    if available_cities:
        bot_city = available_cities[0]
        game_data["used_cities"].add(bot_city)
        game_data["last_letter"] = bot_city[-1] if bot_city[-1] not in "ьъы" else bot_city[-2]
        await message.answer(f"🏙️ Ваш город: {city}\n🤖 Мой ход: {bot_city}. Ваш ход!")
    else:
        await message.answer("🎉 Я не знаю больше городов! Вы победили!")
        del active_games[user_id]

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
