Отчёт о проделанной работе

## 1) model 
   Модель - стандартный алготитм Гатиса. В качестве основы взялы 3 первых слоя от vgg19, иначе не влезало на heroku.
   Классная статья с реализацией - https://towardsdatascience.com/implementing-neural-style-transfer-using-pytorch-fd8d43fb7bfa 
## 2) bot
   Тут ничего примечательного кроме базы данных, чтобы хранить состояния пользователей (код чата - состояние).
   Классная статья по ботам - https://mastergroosha.github.io/telegram-tutorial/docs/lesson_01/
   клавиатура - https://habr.com/ru/sandbox/149884/
## 3) deploying
   задеплоил на Heroky. Подводный камень - при сборке нужно было запихнеть пустой файлик а папку images. Иначе она не собиралась тк была пустая и выдавалась ошибка
   классный видосик по поводу размещения бота на heroku - https://www.youtube.com/watch?v=O0MAWtbg34g