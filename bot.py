import telebot
import config
import dbworker
from model import return_image
from torchvision.utils import save_image
import os

bot = telebot.TeleBot(config.token)
IS_PROCESSING = False

id_images_dict = {}
id_style_dict = {}

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

@bot.message_handler(content_types=["photo"],
                     func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SEND_PIC.value)
def get_pic(message):
    try:
        raw = message.photo[2].file_id
        print(raw)
        got_image_name = raw + ".jpg"
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("./images/" + got_image_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        id_images_dict[message.chat.id] = './images/' + got_image_name

        bot.send_message(message.chat.id, "Изображение получено. Теперь отправьте изображение стиля")
        dbworker.set_state(message.chat.id, config.States.S_SEND_STYLE.value)
        print(id_images_dict)
        print(id_style_dict)
    except:
        print("Error in get image")
        bot.send_message(message.chat.id, "Что-то пошло не так :(")

@bot.message_handler(content_types=["photo"],
                     func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SEND_STYLE.value)
def get_style(message):
    try:
        raw = message.photo[2].file_id
        got_style_name = raw + ".jpg"
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("./images/" + got_style_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        id_style_dict[message.chat.id] = './images/' + got_style_name

        bot.send_message(message.chat.id, "Изображение стиля получено")
        bot.send_message(message.chat.id, "Идёт обработка... Это может занять несколько минут")
        dbworker.set_state(message.chat.id, config.States.S_PROCESSING.value)
        print(id_images_dict)
        print(id_style_dict)
    except:
        print("Error in get style")
        bot.send_message(message.chat.id, "Что-то пошло не так :(")
    try:
        print(1)
        generated_image = return_image(
            id_images_dict[message.chat.id],
            id_style_dict[message.chat.id])
        print(2)
        save_image(generated_image, "./images/"+ str(message.chat.id) +".png")
        print(3)
        bot.send_message(message.chat.id, "Вот ваш результат:")
        bot.send_photo(message.chat.id, open('./images/' + str(message.chat.id) + '.png', 'rb'))
        print(4)
        path = os.path.join('./images/' + str(message.chat.id) + '.png')
        os.remove(path)
        print(5)
        bot.send_message(message.chat.id,
                         "Отлично! Если захочешь пообщаться снова - "
                         "отправь команду /start.")


        dbworker.set_state(message.chat.id, config.States.S_START.value)
    except:
        print("error in processing")
        bot.send_message(message.chat.id,"Что-то пошло не так :(")

bot.infinity_polling()