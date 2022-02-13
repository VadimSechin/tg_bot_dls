import telebot
import config
import dbworker
from model import return_image
from torchvision.utils import save_image
import os
from random import randint
from telebot import types
from flask import Flask, request
import numpy
import io
import PIL
from PIL import Image

TOKEN = config.token
bot = telebot.TeleBot(TOKEN)
# server = Flask(__name__)


IS_PROCESSING = False

id_images_dict = {}
id_style_dict = {}
button_style_dict= {}

@bot.message_handler(commands=["start"])
def cmd_start(message):
    state = dbworker.get_current_state(message.chat.id)
    if state == config.States.S_SEND_PIC.value:
        bot.send_message(message.chat.id, "Отправьте изображение, На которе хотите наложить стиль")
    elif state == config.States.S_SEND_STYLE.value:
        bot.send_message(message.chat.id, "Отправьте изображение стиля")
    elif state == config.States.S_PROCESSING.value:
        bot.send_message(message.chat.id, "Идёт обработка. Ждите")
    else:
        bot.send_message(message.chat.id, "Отправьте изображение, На которе хотите наложить стиль")
        dbworker.set_state(message.chat.id, config.States.S_SEND_PIC.value)

@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Отправьте изображение, На которе хотите наложить стиль")
    dbworker.set_state(message.chat.id, config.States.S_SEND_PIC.value)

def choose_style_bttn():
    keyboard = types.InlineKeyboardMarkup(row_width=1)  # вывод кнопок в 1 колонку
    one = types.InlineKeyboardButton('Пикассо', callback_data='1')
    two = types.InlineKeyboardButton('Лунная ночь Ван Гог', callback_data='2')
    three = types.InlineKeyboardButton('Свой стиль', callback_data='3')
    keyboard.add(one, two, three)
    return keyboard

def accept_style_bttn():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    one = types.InlineKeyboardButton('Хочу этот', callback_data='4')
    two = types.InlineKeyboardButton('Выбрать другой стиль', callback_data='5')
    keyboard.add(one, two)
    return keyboard

@bot.message_handler(content_types=["photo"],
                     func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SEND_PIC.value)
def get_pic(message):
    raw = message.photo[-1].file_id
    print(raw)
    got_image_name = raw + ".png"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)

    image = Image.open(io.BytesIO(downloaded_file))
    np_im = numpy.array(image)
    print(np_im.shape)
    print(np_im[0])

    id_images_dict[message.chat.id] = np_im
    bot.send_message(message.chat.id, "Изображение получено")

    keyboard = choose_style_bttn()
    bot.send_message(message.chat.id, 'Выберете стиль, который хотите наложить', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def logic_inline(call):
    if (dbworker.get_current_state(call.message.chat.id) == config.States.S_SEND_PIC.value):
        if call.data == '1':
            keyboard = accept_style_bttn()
            bot.send_photo(call.message.chat.id, open('./default_styles/' + 'PICASSO.jpg', 'rb'))
            img = PIL.Image.open('./default_styles/' + 'PICASSO.jpg')
            imgarr = numpy.array(img)
            print(imgarr.shape)
            id_style_dict[call.message.chat.id] = imgarr
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
        elif call.data == '4':
            dbworker.set_state(call.message.chat.id, config.States.S_SEND_STYLE.value)
            make_result_pic(call.message.chat.id)
            dbworker.set_state(call.message.chat.id, config.States.S_START.value)
        elif call.data == '5':
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.delete_message(call.message.chat.id, call.message.id-1)
    bot.answer_callback_query(call.id)



@bot.message_handler(content_types=["photo"],
                   func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SEND_STYLE.value)
def get_style(message):
    print('akakakakakaakakakakk')
    raw = message.photo[-1].file_id
    got_style_name = raw + ".jpg"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)

    id_style_dict[message.chat.id] = downloaded_file
    make_result_pic(message.chat.id)


def make_result_pic(id):
    random = randint(1, 9999999)
    bot.send_message(id, "Изображение стиля получено")
    bot.send_message(id, "Идёт обработка... Это может занять несколько минут")
    dbworker.set_state(id, config.States.S_PROCESSING.value)

    generated_image = return_image(
      id_images_dict[id],
      id_style_dict[id])
    save_image(generated_image, "./images/" + str(random) + str(id) + ".png")
    bot.send_message(id, "Вот ваш результат:")
    bot.send_photo(id, open('./images/' + str(random) + str(id) + '.png', 'rb'))
    path = os.path.join('./images/' + str(random) + str(id) + '.png')
    os.remove(path)
    bot.send_message(id,
                   "Отлично! Если захочешь пообщаться снова - отправь команду /start.")
    dbworker.set_state(id, config.States.S_START.value)
bot.remove_webhook()
bot.polling(none_stop=True, interval=0, timeout=50)


#
# @server.route('/' + TOKEN, methods=['POST'])
# def getMessage():
#     json_string = request.get_data().decode('utf-8')
#     update = telebot.types.Update.de_json(json_string)
#     bot.process_new_updates([update])
#     return "!", 200
#
#
# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url='https://polar-tor-49578.herokuapp.com/' + TOKEN)
#     #bot.set_webhook(url='http://192.168.43.124:5000/' + TOKEN)
#     return "!", 200
#
#
# if __name__ == "__main__":
#     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))