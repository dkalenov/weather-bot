from aiogram import Bot, Dispatcher, types #  interacting with the Telegram Bot API
from aiogram.contrib.fsm_storage.memory import MemoryStorage # storing and retrieving user data
from aiogram.dispatcher import FSMContext # storing and accessing data related to the state of the conversation with a user
from aiogram.dispatcher.filters.state import State, StatesGroup # defining and managing states in a finite state machine (FSM)
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton # creating custom keyboards for Telegram bot
from aiogram.utils import executor # starting the event loop and beginning polling for updates from the Telegram Bot API
from config import BOT_TOKEN
from weather_def import *

# API Telegram bot token
bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage() # storing and retrieving user data in memory
dp = Dispatcher(bot, storage=storage) # receiving incoming updates from the Telegram Bot API and routing them to the appropriate handlers

# subclass of StatesGroup using to store and retrieve data
class CityForecast(StatesGroup):
    now_weather = State()
    num_24hours = State()
    num_days5 = State()

# Reply keyboards
quick_reply_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="now"),
            KeyboardButton(text="24 hours"),
            KeyboardButton(text="5 days")
        ]
    ],
    resize_keyboard=True
)


# starting bot
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    text = "Hi there\U0001F44B I'm a weather bot. What period of time do you want to know the weather for?"
    await message.reply(text, reply_markup=quick_reply_buttons)


# defining a user input about the period of time
@dp.message_handler(lambda message: message.text in ["now", "24 hours", "5 days"], state=None)
async def get_num_days(message: types.Message):

# getting a current weather forecast
    if message.text == "now":
      # setting the conversation state to now_weather and prompting the user to provide the name of the city
        await CityForecast.now_weather.set()
        await message.reply("Please tell the name of the city you want to get the weather in")

        @dp.message_handler(state=CityForecast.now_weather) # saving city's name state to now_weather
        async def current_weather(message: types.Message, state: FSMContext):
            try:
                city = message.text.capitalize()
                weather_response = get_current_weather(city)
                await message.answer(weather_response)
                await message.answer("For what period of time do you still want to know the weather?",\
                                     reply_markup=quick_reply_buttons)
                # Clean up state after handling it
                await state.finish()


            except Exception as e:
                await message.reply("\U00002620 Check the city's name input plz! And try it again\U00002620\n"
                                "Or if you want to choose other time period, press /cancel")
                if message == "/cancel":
                    await state.finish()


# getting the weather forecast for 24 hours
    elif message.text == "24 hours":
      # setting the conversation state to now_weather and prompting the user to provide the name of the city
        await CityForecast.num_24hours.set()
        await message.reply("Please tell the name of the city you want to get the weather in")

        @dp.message_handler(state=CityForecast.num_24hours) # saving city's name state to num_24hours
        async def get_24weather(message: types.Message, state: FSMContext):
            try:
                city = message.text.capitalize()
                weather_response = get_24_hours_weather(city)
                await message.answer(weather_response)
                await message.answer("For what period of time do you still want to know the weather?",\
                                     reply_markup=quick_reply_buttons)
                # Clean up state after handling it
                await state.finish()

            except Exception as e:
                await message.reply("\U00002620 Check the city's name input plz! And try it again\U00002620\n"
                                "Or if you want to choose other time period, press /cancel")
                if message == "/cancel":
                    await state.finish()


# getting the weather forecast for 5 days
    elif message.text == "5 days":
      # setting the conversation state to num_days5 and prompting the user to provide the name of the city
        await CityForecast.num_days5.set()
        await message.reply("Please tell the name of the city you want to get the weather in")

        @dp.message_handler(state=CityForecast.num_days5)
        async def handle_city_for_5_days(message: types.Message, state: FSMContext):
            try:
                city = message.text.capitalize()
                weather_response = get_5days_forecast(city)
                await message.answer(weather_response)
                await message.answer("For what period of time do you still want to know the weather?",\
                                     reply_markup=quick_reply_buttons)
                # Clean up state after handling it
                await state.finish()

            except Exception as e:
                await message.reply("\U00002620 Check the city's name input plz! And try it again\U00002620\n"
                                "Or if you want to choose other time period, press /cancel")
                if message == "/cancel":
                    await state.finish()


# cancelling of time period choice
@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish() # finish current_state
    await message.reply(f'ОК, boss!\nWhat period of time do you still want to know the weather for?',\
                        reply_markup=quick_reply_buttons)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)