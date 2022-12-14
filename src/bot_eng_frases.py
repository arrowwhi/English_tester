import asyncio
from sys import exit
import sqlite3
from sqlite3 import Error
from random import randint
import random
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BotBlocked
from config import TOKEN            #, admin_id, database_dir
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import db_frases
# from db_frases import create_connection, execute_query, create_table, execute_read_query

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
connection = db_frases.create_connection("cards.db")

class StateFrases(StatesGroup):
    take_frase = State()
    wait_rus_frase = State()
    wait_eng_frase = State()
    add_frase_confirm = State()
    wait_rus_answer = State()
    wait_eng_answer = State()
    delete_frases = State()



def main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("Получить фразу на английском")
    b2 = KeyboardButton("Получить фразу на русском")
    b3 = KeyboardButton("Добавить фразу")
    b4 = KeyboardButton("Удалить фразу")
    b5 = KeyboardButton("Получить все фразы")
    b0 = KeyboardButton("Отменить")
    kb.row(b1,b2)
    kb.row(b3,b4,b5)
    kb.add(b0)
    return kb

def cancel_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("Отменить")
    kb.add(b1)
    return kb

def confirm_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("Отменить")
    b0 = KeyboardButton("Добавляем")
    kb.add(b0,b1)
    return kb

def ans_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("Отменить")
    b2 = KeyboardButton("Узнать ответ")
    kb.add(b1)
    kb.add(b2)
    return kb

async def get_all_frases(message: types.Message):
    pass
    frases = db_frases.execute_read_query(connection,db_frases.get_all_frases())
    count = db_frases.execute_read_query(connection,db_frases.rows_rows())[0][0]
    if count==0:
        await message.answer("Фраз нет!", reply_markup=main_keyboard())
        return
    i = 0
    while(i <= count-1):
        text = ""
        for j in range(3):
            if i+j >= count:
                break
            text += str(frases[i+j][0])+".\n" + frases[i+j][1] + "\n - \n" + frases[i+j][2] + "\n-------------\n"
        await message.answer(text, reply_markup=main_keyboard())
        i+=3
        time.sleep(1)



async def process_start_command(message: types.Message, state: FSMContext):
    await message.answer("Привет! Выбери кнопку на клавиатуре", reply_markup=main_keyboard())
    await StateFrases.take_frase.set()

async def process_get_frase_eng(message: types.Message, state: FSMContext):
    count = db_frases.execute_read_query(connection,db_frases.rows_rows())
    if count==0:
        await message.answer("Фраз нет!", reply_markup=main_keyboard())
        return
    number = random.randint(0,count[0][0]-1)
    frase = db_frases.execute_read_query(connection,db_frases.get_all_frases())[number]

    await message.answer("Вот фраза:\n" + str(frase[1]), reply_markup=ans_keyboard())
    rus_frase = str(frase[2]).lower()
    await state.update_data(rus_frase=rus_frase)
    await message.answer("\n\nТеперь введи ее на русском")
    await StateFrases.wait_rus_answer.set()

async def confirm_rus_frase(message: types.Message, state: FSMContext):
    fr = message.text.lower()
    user_data = await state.get_data()

    if fr == user_data["rus_frase"]:
        await message.answer("Правильно!")
        await StateFrases.take_frase.set()
        await message.answer("Выбери кнопку на клавиатуре", reply_markup=main_keyboard())
    else:
        await message.answer("Неправильно! Попробуй еще", reply_markup=ans_keyboard())

async def show_rus_frase(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer("Правильный ответ:\n" + user_data["rus_frase"] , reply_markup=main_keyboard())
    await StateFrases.take_frase.set()

async def show_eng_frase(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer("Правильный ответ:\n" + user_data["eng_frase"] , reply_markup=main_keyboard())
    await StateFrases.take_frase.set()


async def process_get_frase_rus(message: types.Message, state: FSMContext):
    count = db_frases.execute_read_query(connection,db_frases.rows_rows())
    if count==0:
        await message.answer("Фраз нет!", reply_markup=main_keyboard())
        return
    number = random.randint(0,count[0][0]-1)
    frase = db_frases.execute_read_query(connection,db_frases.get_all_frases())[number]

    await message.answer("Вот фраза:\n" + str(frase[2]), reply_markup=ans_keyboard())
    eng_frase = str(frase[1]).lower()
    await state.update_data(eng_frase=eng_frase)

    await message.answer("\n\nТеперь введи ее на английском")
    await StateFrases.wait_eng_answer.set()

async def confirm_eng_frase(message: types.Message, state: FSMContext):
    fr = message.text.lower()
    user_data = await state.get_data()

    if fr == user_data["eng_frase"]:
        await message.answer("Правильно!")
        await StateFrases.take_frase.set()
        await message.answer("Выбери кнопку на клавиатуре", reply_markup=main_keyboard())
    else:
        await message.answer("Неправильно! Попробуй еще", reply_markup=ans_keyboard())


async def take_frase(message: types.Message, state: FSMContext):
    pass
    await message.answer("Введи фразу на английском", reply_markup=cancel_keyboard())
    await StateFrases.wait_eng_frase.set()

async def take_frase_eng(message: types.Message, state: FSMContext):
    eng_frase = message.text
    await message.answer("Фраза на английском:\n" + str(eng_frase))
    await state.update_data(eng_frase=eng_frase)
    await message.answer("Введи фразу на русском", reply_markup=cancel_keyboard())
    await StateFrases.wait_rus_frase.set()

async def take_frase_rus(message: types.Message, state: FSMContext):
    rus_frase = message.text
    user_data = await state.get_data()
    msg = "Фраза на английском:\n" + user_data["eng_frase"]\
          + "\n\nФраза на русском:\n" + rus_frase   \
          + "\n\nДобавляем?"
    await message.answer(msg, reply_markup=confirm_keyboard())
    await state.update_data(rus_frase=rus_frase)
    await StateFrases.add_frase_confirm.set()

async def confirm_add(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    db_frases.execute_query(connection, db_frases.add_value(user_data["eng_frase"], user_data["rus_frase"]))
    await message.answer("Успешно добавлено")
    await message.answer("Выбери кнопку на клавиатуре", reply_markup=main_keyboard())
    await StateFrases.take_frase.set()

async def press_cancel(message: types.Message, state: FSMContext):
    await message.answer("Нажата отмена")
    await message.answer("Выбери кнопку на клавиатуре", reply_markup=main_keyboard())
    await StateFrases.take_frase.set()
  
async def delete_values(message: types.Message, state: FSMContext):
    await get_all_frases(message)
    await message.answer("укажите номера фраз, которые хотите удалить(через пробел)", reply_markup=cancel_keyboard())
    await StateFrases.delete_frases.set()

async def confirm_delete(message: types.Message, state: FSMContext):
    lis = message.text.split()
    for i in lis:
        db_frases.execute_query(connection, db_frases.delete_value(int(i)))
    await message.answer("Фразы успешно удалены!", reply_markup=main_keyboard())
    await StateFrases.take_frase.set()


def inline_register_handlers_booking(dp: Dispatcher):
    dp.register_message_handler(
        process_start_command, commands="start", state="*")
    dp.register_message_handler(
        press_cancel, state="*", text="Отменить")
    dp.register_message_handler(
        get_all_frases, state=StateFrases.take_frase, text="Получить все фразы")
    dp.register_message_handler(
        delete_values, state=StateFrases.take_frase, text="Удалить фразу")   
    dp.register_message_handler(
        confirm_delete, state=StateFrases.delete_frases)     
    dp.register_message_handler(
        process_get_frase_eng, state=StateFrases.take_frase, text="Получить фразу на английском")
    dp.register_message_handler(
        show_rus_frase, state=StateFrases.wait_rus_answer, text="Узнать ответ")
    dp.register_message_handler(
        confirm_rus_frase, state=StateFrases.wait_rus_answer)
    dp.register_message_handler(
        process_get_frase_rus, state=StateFrases.take_frase, text="Получить фразу на русском")
    dp.register_message_handler(
        show_eng_frase, state=StateFrases.wait_eng_answer, text="Узнать ответ")
    dp.register_message_handler(
        confirm_eng_frase, state=StateFrases.wait_eng_answer)
    dp.register_message_handler(
        take_frase, state=StateFrases.take_frase, text="Добавить фразу")
    dp.register_message_handler(
        take_frase_eng, state=StateFrases.wait_eng_frase)
    dp.register_message_handler(
        take_frase_rus, state=StateFrases.wait_rus_frase)
    dp.register_message_handler(
        confirm_add, state=StateFrases.add_frase_confirm, text="Добавляем")
    

inline_register_handlers_booking(dp)


if __name__ == '__main__':
    db_frases.execute_query(connection, db_frases.create_table())
    executor.start_polling(dp)
    a = input()
    print(a)
