import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.methods.send_photo import SendPhoto
from aiogram.methods.send_message import SendMessage
from aiogram.methods.edit_message_reply_markup import EditMessageReplyMarkup
from aiogram.methods.edit_message_text import EditMessageText
from aiogram.methods.delete_my_commands import DeleteMyCommands
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import KeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import Message, InlineKeyboardButton, FSInputFile, bot_command
import dbwork as db
from loader import loop
from datetime import datetime



bot = Bot(os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()
load_dotenv()

facecontrol = KeyboardBuilder(button_type=InlineKeyboardButton)
facecontrol.button(text='✅ Добавить', callback_data='add_user')
facecontrol.button(text='❌ Забанить', callback_data='ban_user')

ready_button = KeyboardBuilder(button_type=InlineKeyboardButton)
ready_button.button(text='⁉️ Готов/Ready', callback_data='ready')

accepted_button = KeyboardBuilder(button_type=InlineKeyboardButton)
accepted_button.button(text='✅ Принято/Accepted', callback_data='#')

delete_button = KeyboardBuilder(button_type=InlineKeyboardButton)
delete_button.button(text='❌ Удалить', callback_data='delete')

admin_button = ReplyKeyboardBuilder()
admin_button.button(text='/Отправить_матч')
admin_button.button(text='/Отправить_исход')
admin_button.button(text='/Написать_всем')
admin_button.button(text='/Кто_в_боте')
admin_button.button(text='/Кто_готов')
admin_button.adjust(1,2,2)

class Form(StatesGroup):
    outcome = State()
    text = State()

@dp.callback_query()
async def  callback_query_keyboard(callback_query: types.callback_query):
  if callback_query.data == 'add_user':
    username = callback_query.message.text.split("от")[1].split("|")[0].strip().replace('@','')
    chat_id = callback_query.message.text.split("от")[1].split("|")[1].strip()
    await DB.upd_user('approved',username)
    await bot(EditMessageText(text=f'✅ {username} добавлен', chat_id = callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=None))
    await bot(SendMessage(chat_id = chat_id, text = "Hello. Instructions for using the bot. Everything is easy and simple. The game comes to you. If you can place a bet, click on the Ready button and wait for the information in the bot. After the bet, write the bet amount to the Aggressor. Important! If you cannot place a bet, do not click on the Ready button."))
  elif callback_query.data == 'ban_user':
    username = callback_query.message.text.split("от")[1].split("|")[0].strip().replace('@','')
    await DB.upd_user('banned',username)
    await bot(EditMessageText(text=f'❌ @{username} забанен', chat_id = callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=None))
  elif callback_query.data == 'ready':
    await DB.upd_user_ready(callback_query.from_user.id)
    await bot(EditMessageReplyMarkup(chat_id = callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=accepted_button.as_markup()))
  elif callback_query.data == 'delete':
    await DB.del_user(callback_query.message.text.replace('@',''))
    await bot(EditMessageText(text=f'✅ {callback_query.message.text} удалён', chat_id = callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=None))



@dp.message(CommandStart())
async def cmd_start(message: Message):
  username = message.from_user.username
  chat_id = message.from_user.id
  if username is not None:
    check = await DB.get_user(username)
    if check is None:
      admin = await DB.get_admin()
      await DB.add_user(chat_id, username)
      await bot(SendMessage(chat_id=admin['chat_id'],text=f'Запрос на добавление от @{username} | {chat_id}',reply_markup=facecontrol.as_markup()))
      await message.answer(f'An add request has been sent to the administrator. Pending review')
    else:
      if check['status'] == 'waiting':
        await message.answer(f'Your request for addition is already under review.')
      elif check['status'] == 'approved':
        await message.answer(f'You have already been added to this bot')
      elif check['status'] == 'banned':
        await message.answer(f'You are banned from this bot. Use is prohibited')
  else:
    await message.answer(f'Please fill in the username in the telegram settings and try adding it again')


@dp.message(F.text, Command("Кто_готов"))
async def whois_ready(message: Message):
  user = await DB.get_user(message.from_user.username)
  if user['role'] == 'admin':
    ready_users = await DB.get_ready()
    if len(ready_users) > 0:
      text = ''
      for user in ready_users:
        text += f"@{user['username']}\n"
    else:
      text = 'Список подписавшихся пуст'
    await message.answer(f'{text}')


@dp.message(F.text, Command("Кто_в_боте"))
async def show_users(message: Message):
  user = await DB.get_user(message.from_user.username)
  if user['role'] == 'admin':
    users = await DB.get_all_users()
    if len(users) > 0:
      for user in users:
        await message.answer(text=f"@{user['username']}",reply_markup=delete_button.as_markup())
    else:
      await message.answer(text = 'Список пользователей пуст')
    


@dp.message(F.text, Command("Отправить_матч"))
async def send_match(message: Message):
  user = await DB.get_user(message.from_user.username)
  if user['role'] == 'admin':
    await DB.clear_user_ready()
    users = await DB.get_not_ready()
    if len(users) > 0:
      await message.answer(f'Рассылаю запрос {len(users)} пользователям')
      for user in users:
        try:
          await bot(SendPhoto(chat_id = user['chat_id'],photo=FSInputFile("example.jpg"), reply_markup=ready_button.as_markup()))
        except Exception as e:
          logging.warning(f'{user} - {e}')
      await message.answer(f'Запрос разослан')
    else:
      await message.answer(f'Нет пользователей для рассылки')


@dp.message(F.text, Command("Написать_всем"))
async def send_text(message: Message, state: FSMContext):
  user = await DB.get_user(message.from_user.username)
  if user['role'] == 'admin':
    await state.set_state(Form.text)
    await message.answer(f'Введите сообщение или напишите отмена для выхода')


@dp.message(F.text, Command("Отправить_исход"))
async def send_outcome(message: Message, state: FSMContext):
  user = await DB.get_user(message.from_user.username)
  if user['role'] == 'admin':
    await state.set_state(Form.outcome)
    await message.answer(f'Введите исход или напишите отмена для выхода')


@dp.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
  """
  Разрешить пользователю отменить любое действие
  """
  current_state = await state.get_state()
  if current_state is None:
      return
  logging.info("Отменяем state %r", current_state)
  await state.clear()
  await message.answer(f'Действие отменено')


@dp.message(Form.outcome)
async def process_text(message: Message, state: FSMContext):
  user = await DB.get_user(message.from_user.username)
  if user['role'] == 'admin':
    users = await DB.get_ready()
    await message.answer(f'Рассылаю исход {len(users)} пользователям')
    for user in users:
      try:
        await bot(SendMessage(chat_id = user['chat_id'], text = f"{message.text}"))
      except Exception as e:
        logging.warning(f'{user} - {e}')
    await message.answer(f'Исход разослан')
    await state.clear()


@dp.message(Form.text)
async def process_text(message: Message, state: FSMContext):
  user = await DB.get_user(message.from_user.username)
  if user['role'] == 'admin':
    users = await DB.get_all_approved_users()
    await message.answer(f'Рассылаю сообщение {len(users)} пользователям')
    for user in users:
      try:
        await bot(SendMessage(chat_id = user['chat_id'], text = f"{message.text}"))
      except Exception as e:
        logging.warning(f'{user} - {e}')
    await message.answer(f'Сообщение разослано')
    await state.clear()


@dp.message()
async def get_commands(message: Message):
  user = await DB.get_user(message.from_user.username)
  if user is not None and  user['role'] == 'admin':
    await message.answer(f'Клавиатура подключена', reply_markup=admin_button.as_markup())


async def main():
  date = datetime.now().strftime('%d%m_%H%M')
  work_dir = os.path.abspath(os.path.dirname(__file__))
  file_path = f"{work_dir}//log"
  logging.basicConfig(filename=f"{file_path}//{date}.log", encoding='utf-8', level=logging.INFO, format = "%(asctime)s - %(levelname)s - %(message)s", datefmt='%d.%m.%Y %H:%M:%S')
  await dp.start_polling(bot)


if __name__ == '__main__':
  DB = db.DBCommands()
  loop.run_until_complete(main())
  