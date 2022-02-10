import telebot
import config
import dbworker
from model import return_image
from torchvision.utils import save_image
import os
from random import randint
from telebot import types

bot = telebot.TeleBot(config.token)
IS_PROCESSING = False

id_images_dict = {}
id_style_dict = {}
button_style_dict= {}

# Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    state = dbworker.get_current_state(message.chat.id)
    if state == config.States.S_SEND_PIC.value:
        bot.send_message(message.chat.id, "Отправьте изображение, На которе хотите наложить стиль")
    elif state == config.States.S_SEND_STYLE.value:
        bot.send_message(message.chat.id, "Отправьте изображение стиля")
    elif state == config.States.S_PROCESSING.value:
        bot.send_message(message.chat.id, "Идёт обработка. Ждите")
    else:  # Под "остальным" понимаем состояние "0" - начало диалога
        bot.send_message(message.chat.id, "Отправьте изображение, На которе хотите наложить стиль")
        dbworker.set_state(message.chat.id, config.States.S_SEND_PIC.value)

# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Отправьте изображение, На которе хотите наложить стиль")
    dbworker.set_state(message.chat.id, config.States.S_SEND_PIC.value)

def choose_style_bttn():
    keyboard = types.InlineKeyboardMarkup(row_width=1)  # вывод кнопок в 1 колонку
    one = types.InlineKeyboardButton('Пикассо', callback_data='1')
    two = types.InlineKeyboardButton('Лунная ночь Ван Гог', callback_data='2')
    three = types.InlineKeyboardButton('Свой стиль', callback_data='3')
    # и так далее либо же сделать через цикл for, но у каждой кнопки должен быть свой callback
    keyboard.add(one, two, three)
    return keyboard

def accept_style_bttn():
    keyboard = types.InlineKeyboardMarkup(row_width=1)  # вывод кнопок в 1 колонку
    one = types.InlineKeyboardButton('Хочу этот', callback_data='4')
    two = types.InlineKeyboardButton('Выбрать другой стиль', callback_data='5')
    # и так далее либо же сделать через цикл for, но у каждой кнопки должен быть свой callback
    keyboard.add(one, two)
    return keyboard

@bot.message_handler(content_types=["photo"],
                     func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SEND_PIC.value)
def get_pic(message):
    raw = message.photo[-1].file_id
    print(raw)
    got_image_name = raw + ".jpg"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("./images/" + got_image_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    id_images_dict[message.chat.id] = './images/' + got_image_name

    bot.send_message(message.chat.id, "Изображение получено")
    # dbworker.set_state(message.chat.id, config.States.S_SEND_STYLE.value)
    print(id_images_dict)
    print(id_style_dict)

    keyboard = choose_style_bttn()
    bot.send_message(message.chat.id, 'Выберете стиль, который хотите наложить', reply_markup=keyboard)
    print(message.chat.id)
    # except:
    #     print("Error in get image")
    #     bot.send_message(message.chat.id, "Что-то пошло не так :(")



@bot.callback_query_handler(func=lambda call: True)
def logic_inline(call):
    if (dbworker.get_current_state(call.message.chat.id) == config.States.S_SEND_PIC.value):
        if call.data == '1':
            keyboard = accept_style_bttn()
            bot.send_photo(call.message.chat.id, open('./default_styles/' + 'PICASSO.jpg', 'rb'))
            id_style_dict[call.message.chat.id] = './default_styles/' + 'PICASSO.jpg'
            bot.send_message(call.message.chat.id, 'Пойдёт?', reply_markup=keyboard)
            print(id_images_dict)
            print(id_style_dict)
        elif call.data == '2':
            keyboard = accept_style_bttn()
            bot.send_photo(call.message.chat.id, open('./default_styles/' + 'VG_MN.jpg', 'rb'))
            id_style_dict[call.message.chat.id] = './default_styles/' + 'VG_MN.jpg'
            bot.send_message(call.message.chat.id, 'Пойдёт?', reply_markup=keyboard)
            print(id_images_dict)
            print(id_style_dict)
        elif call.data == '3':
            bot.send_message(call.message.chat.id, 'Пришлите изображение стиля')
            dbworker.set_state(call.message.chat.id, config.States.S_SEND_STYLE.value)
            print(call.message.chat.id)
            dbworker.set_state(call.message.chat.id, config.States.S_START.value)
        elif call.data == '4':
            dbworker.set_state(call.message.chat.id, config.States.S_SEND_STYLE.value)
            make_resukt_pic(call.message.chat.id)
            dbworker.set_state(call.message.chat.id, config.States.S_START.value)
        elif call.data == '5':
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.delete_message(call.message.chat.id, call.message.id-1)
    bot.answer_callback_query(call.id)



@bot.message_handler(content_types=["photo"],
                   func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SEND_STYLE.value)
def get_style(message):
    raw = message.photo[-1].file_id
    got_style_name = raw + ".jpg"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("./images/" + got_style_name, 'wb') as new_file:
      new_file.write(downloaded_file)

    id_style_dict[message.chat.id] = './images/' + got_style_name
    make_resukt_pic(message.chat.id)


def make_resukt_pic(id):
    random = randint(1, 9999999)
    bot.send_message(id, "Изображение стиля получено")
    bot.send_message(id, "Идёт обработка... Это может занять несколько минут")
    dbworker.set_state(id, config.States.S_PROCESSING.value)
    print(id_images_dict)
    print(id_style_dict)

    print(1)
    generated_image = return_image(
      id_images_dict[id],
      id_style_dict[id])
    print(2)
    save_image(generated_image, "./images/" + str(random) + str(id) + ".png")
    print(3)
    bot.send_message(id, "Вот ваш результат:")
    bot.send_photo(id, open('./images/' + str(random) + str(id) + '.png', 'rb'))
    print(4)
    path = os.path.join('./images/' + str(random) + str(id) + '.png')
    os.remove(path)
    print(5)
    bot.send_message(id,
                   "Отлично! Если захочешь пообщаться снова - "
                   "отправь команду /start.")

    dbworker.set_state(id, config.States.S_START.value)


bot.infinity_polling()