from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button5 = KeyboardButton(text='Купить')
kb.row(button1, button2)
kb.add(button5)
inkb = InlineKeyboardMarkup(resize_keyboard=True)
inkb2 = InlineKeyboardMarkup(resize_keyboard=True)
button3 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button4 = InlineKeyboardButton(text='Формула расчёта', callback_data='formulas')
product1 = InlineKeyboardButton(text='Продукт 1', callback_data='product_buying')
product2 = InlineKeyboardButton(text='Продукт 2', callback_data='product_buying')
product3 = InlineKeyboardButton(text='Продукт 3', callback_data='product_buying')
product4 = InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
inkb.row(button3, button4)
inkb2.row(product1, product2, product3, product4)


@dp.message_handler(commands=['start'])
async def start_message(message):
    print('Привет! Я бот помогающий твоему здоровью.')
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    print(message.chat.username)
    await message.answer('Выберите опцию:', reply_markup=inkb)
    print(message.answer)


@dp.callback_query_handler(text=['formulas'])
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()


@dp.message_handler(text=['Купить'])
async def get_buying_list(message):
    data = get_all_products()
    for i in range(0, 4):
        await message.answer(f'Название: {data[i][1]} | Описание: {data[i][2]} | Цена: {data[i][3]}')
        with open(f'files/{i + 1}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer(text='Выберите продукт для покупки:', reply_markup=inkb2)


@dp.callback_query_handler(text=['product_buying'])
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text=['calories'])
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    result = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5
    await message.answer(f' Ваша норма каллорий {result}')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
