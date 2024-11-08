from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, default_callback_handler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаём пользовательскю сессию по его id.
    # Если пользователь отправил команду сообщением.
    if update.message:
        # Создаём объект сессии пользователя UserSession.
        user_session = UserSession(update.message.from_user.id)
        # Сохраняем объект в словаре user_sessions ("базе данных") user_sessions.
        save_user_session(user_session)
        # Устанавливаем режим диалога GPT для СonversationHandler в объекте пользовательской сессии.
        user_session.state = START
    # Если пользователь отправил команду кнопкой.
    else:
        # Создаём объект сессии пользователя UserSession.
        user_session = UserSession(update.callback_query.from_user.id)
        # Сохраняем объект в словаре user_sessions ("базе данных") user_sessions.
        save_user_session(user_session)
        # Устанавливаем режим диалога GPT для СonversationHandler в объекте пользовательской сессии.
        user_session.state = START
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'trans': 'Перевести слово или предложение',
        'exit': 'Выйти'
    })
    # Возвращаем значение "режима" диалога для СonversationHandler.
    return user_session.state

# Задание №1. Эхо-бот
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаём переменную text, которой присваиваем полученный от пользователя бота текст.
    text = update.message.text
    # Отправляем назад пользователю полученный текст.
    await send_text(update, context, text)

# Задание №2. Рандомный факт.
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Устанавливаем режим диалога RANDOM для СonversationHandler в объекте пользовательской сессии.
    # Если пользователь отправил команду сообщением.
    if update.message:
        user = update.message.from_user
        user_session = get_user_session(user.id)
        user_session.state = RANDOM
    # Если пользователь отправил команду кнопкой.
    else:
        user = update.callback_query.from_user
        user_session = get_user_session(user.id)
        user_session.state = RANDOM
    # Создаём переменную promt с текстом из файла random папки promtpts
    prompt = load_prompt('random')
    # Создаём переменную text с текстом из файла random папки messages
    text = load_message('random')
    # Ожидаем загрузки картинки random из папки images в бот
    await send_image(update,context,'random')
    # Ожидаем загрузки текста переменной text в бот. Присваиваем значение, чтобы затем можно было изменить.
    await send_text(update, context, text)
    # Устанавливаем prompt для ChatGPT с текстом из переменной prompt (одновременной создаём переменную answer с ответом)
    answer = await chat_gpt.send_question(prompt,'')
    # Получаем ответ ChatGPT и изменяем переменную text в telegram боте.
    # await text_answer.edit_text(answer) # Будет дублироваться, т.к. в функции ниже тоже есть переменная answer.
    # Создаём кнопку 'Ещё один случайный факт->' и 'Закончить и выйти'
    await send_text_buttons(update, context, answer, {'random':'Ещё один случайный факт->',
                                                      'random_end':'Закончить и выйти' })
    # Возвращаем значение "режима" диалога для СonversationHandler.
    return user_session.state # Не работает, если ставлю здесь RANDOM. Почему?

# Создаём метод для обработки действия на нажатие кнопок.
async def random_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ожидаем нажатия кнопки.
    await update.callback_query.answer()
    # Получаем "значение" нажатой кнопки.
    callb = update.callback_query.data
    if callb == "random":
        await random(update, context)
    else:
        await exit_to_start(update, context)

# Задание №3. ChatGPT интерфейс.
async def ch_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем данные пользователя (для id)
    user = update.message.from_user
    # Создаём объект UserSession.
    user_session = get_user_session(user.id)
    # Устанавливаем режим диалога GPT для СonversationHandler в объекте пользовательской сессии.
    user_session.state = GPT
    # Создаём переменную promt с текстом из файла gpt папки promtpts
    prompt = load_prompt('gpt')
    # Создаём переменную text с текстом из файла gpt папки messages
    text = load_message('gpt')
    # Устанавливаем prompt для ChatGPT
    chat_gpt.set_prompt(prompt)
    # Ожидаем загрузки картинки gpt из папки images в бот
    await send_image(update,context,'gpt')
    # Ожидаем загрузки текста переменной text в бот.
    await send_text(update, context, text)
    # Возвращаем режим диалога для СonversationHandler.
    return user_session.state #Не работает, если ставлю здесь GPT. Почему?

# Создаём метод для общения с ChatGPT
async def gpt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ожидаем загрузки текста переменной text в бот. Присваиваем значение, чтобы затем можно было изменить.
    text = update.message.text
    # Выводит в телеграм бот строку "Готовлю ответ на ваш вопрос..."
    text_answer = await send_text(update, context, "Готовлю ответ на ваш вопрос...")
    # Делаем запрос к ChatGPT с текстом из телеграм бота (одновременной создаём переменную answer с ответом)
    answer = await chat_gpt.add_message(text)
    # Получаем ответ ChatGPT и изменяем переменную text_answer в telegram боте.
    await text_answer.edit_text(answer)

# Задание №4. Диалог с известной личностью.
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если пользователь отправил команду сообщением.
    if update.message:
        # Получаем данные пользователя (для id)
        user = update.message.from_user
        # Создаём объект UserSession.
        user_session = get_user_session(user.id)
        # Устанавливаем режим диалога TALK для СonversationHandler в объекте пользовательской сессии.
        user_session.state = TALK
    # Если пользователь отправил команду кнопкой.
    else:
        # Получаем данные пользователя (для id)
        user = update.callback_query.from_user
        # Создаём объект UserSession.
        user_session = get_user_session(user.id)
        # Устанавливаем режим диалога TALK для СonversationHandler в объекте пользовательской сессии.
        user_session.state = TALK
    # Создаём переменную text с текстом из файла talk папки messages
    text = load_message('talk')
    # Ожидаем загрузки картинки talk из папки images в бот
    await send_image(update,context,'talk')
    # Создаём кнопки для взаимодействия с пользователем
    await send_text_buttons(update, context, text, {'cob_talk': 'Курт Кобейн', 'que_talk': 'Елизавета II', 'tol_talk': 'Джон Толкиен', 'nie_talk': 'Фридрих Ницше', 'haw_talk': 'Стивен Хокинг'})
    # Возвращаем значение "режима" диалога для СonversationHandler.
    return user_session.state  # Не работает, если ставлю здесь TALK. Почему?

# Создаём метод для общения с ChatGPT
async def talk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ожидаем загрузки текста переменной text в бот. Присваиваем значение, чтобы затем можно было изменить.
    text = update.message.text
    # Выводит в телеграм бот строку "Дайте подумать..."
    text_answer = await send_text(update, context, "Дайте подумать...")
    # Делаем запрос к ChatGPT с текстом из телеграм бота (одновременной создаём переменную answer с ответом)
    answer = await chat_gpt.add_message(text)
    # Получаем ответ ChatGPT и изменяем переменную text_answer в telegram боте.
    await text_answer.edit_text(answer)

# Создаём метод для обработки действия на нажатие кнопок.
async def talk_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ожидаем нажатия кнопки.
    await update.callback_query.answer()
    # Получаем "значение" нажатой кнопки.
    callb = update.callback_query.data
    if callb == "cob_talk":
        # Создаём переменную promt с текстом из соответствующего файла папки promtpts
        prompt = load_prompt('talk_cobain')
        # Устанавливаем prompt для ChatGPT
        chat_gpt.set_prompt(prompt)
        # Ожидаем загрузки картинки из папки images в бот
        await send_image(update, context, 'talk_cobain')
        # Ожидаем вопрос пользователя бота
        await send_text(update, context, 'Какой вопрос вы бы хотели мне задать?')
    elif callb == "que_talk":
        # Создаём переменную promt с текстом из соответствующего файла папки promtpts
        prompt = load_prompt('talk_queen')
        # Устанавливаем prompt для ChatGPT
        chat_gpt.set_prompt(prompt)
        # Ожидаем загрузки картинки из папки images в бот
        await send_image(update, context, 'talk_queen')
        # Ожидаем вопрос пользователя бота
        await send_text(update, context, 'Какой вопрос вы бы хотели мне задать?')
    elif callb == "tol_talk":
        # Создаём переменную promt с текстом из соответствующего файла папки promtpts
        prompt = load_prompt('talk_tolkien')
        # Устанавливаем prompt для ChatGPT
        chat_gpt.set_prompt(prompt)
        # Ожидаем загрузки картинки из папки images в бот
        await send_image(update, context, 'talk_tolkien')
        # Ожидаем вопрос пользователя бота
        await send_text(update, context, 'Какой вопрос вы бы хотели мне задать?')
    elif callb == "nie_talk":
        # Создаём переменную promt с текстом из соответствующего файла папки promtpts
        prompt = load_prompt('talk_nietzsche')
        # Устанавливаем prompt для ChatGPT
        chat_gpt.set_prompt(prompt)
        # Ожидаем загрузки картинки из папки images в бот
        await send_image(update, context, 'talk_nietzsche')
        # Ожидаем вопрос пользователя бота
        await send_text(update, context, 'Какой вопрос вы бы хотели мне задать?')
    elif callb == "haw_talk":
        # Создаём переменную promt с текстом из соответствующего файла папки promtpts
        prompt = load_prompt('talk_hawking')
        # Устанавливаем prompt для ChatGPT
        chat_gpt.set_prompt(prompt)
        # Ожидаем загрузки картинки из папки images в бот
        await send_image(update, context, 'talk_hawking')
        # Ожидаем вопрос пользователя бота
        await send_text(update, context, 'Какой вопрос вы бы хотели мне задать?')
    else:
        await exit_to_start(update, context)

# Задание №5. Квиз.
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если пользователь отправил команду сообщением.
    if update.message:
        # Получаем данные пользователя (для id)
        user = update.message.from_user
        # Создаём объект UserSession.
        user_session = get_user_session(user.id)
        # Устанавливаем режим диалога QUIZ для СonversationHandler в объекте пользовательской сессии.
        user_session.state = QUIZ
        # Создаём счётчик правильных ответов
        user_session.right = 0
        # Создаём счётчик количества вопросов
        user_session.sum = 0
    # Если пользователь отправил команду кнопкой.
    else:
        # Получаем данные пользователя (для id)
        user = update.callback_query.from_user
        # Создаём объект UserSession.
        user_session = get_user_session(user.id)
        # Устанавливаем режим диалога QUIZ для СonversationHandler в объекте пользовательской сессии.
        user_session.state = QUIZ
        # Создаём счётчик правильных ответов
        user_session.right = 0
        # Создаём счётчик количества вопросов
        user_session.sum = 0
    # Создаём переменную promt с текстом из файла gpt папки promtpts
    prompt = load_prompt('quiz')
    # Создаём переменную text с текстом из файла quiz папки messages
    text = load_message('quiz')
    # Устанавливаем prompt для ChatGPT
    chat_gpt.set_prompt(prompt)
    # Ожидаем загрузки картинки quiz из папки images в бот
    await send_image(update,context,'quiz')
    # Создаём кнопки для взаимодействия с пользователем
    await send_text_buttons(update, context, text, {'quiz_prog': 'Программирование на языке Python', 'quiz_math': 'Математические теории', 'quiz_biology': 'Биология', 'quiz_more': 'Повтор последней темы'})
    # Возвращаем значение "режима" диалога для СonversationHandler.
    return user_session.state  # Не работает, если ставлю здесь QUIZ. Почему?

# Создаём метод для общения с ChatGPT
async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ожидаем загрузки текста переменной text в бот. Присваиваем значение, чтобы затем можно было изменить.
    text = update.message.text
    # Делаем запрос к ChatGPT с текстом из телеграм бота (одновременной создаём переменную answer с ответом)
    answer = await chat_gpt.add_message(text)
    # Увеличиваем счётчик правильных ответов и счётчик количества вопросов на единицу, если дан правильный ответ.
    if answer == 'Правильно!':
        user = update.message.from_user
        user_session = get_user_session(user.id)
        user_session.sum += 1
        user_session.right += 1
        sum_q = user_session.sum
        right = user_session.right
        # Кнопки для выбора тематики следующего вопроса.
        await send_text_buttons(update, context, answer,
                                {'quiz_prog': 'Программирование на языке Python',
                                 'quiz_math': 'Математические теории',
                                 'quiz_biology': 'Биология',
                                 'quiz_more': 'Повтор последней темы'})
        # Вывод счётчиков в окно бота.
        await send_text(update, context, f'Количество вопросов: {sum_q}')
        await send_text(update, context, f'Количество првильных ответов: {right}')
    else:
        user = update.message.from_user
        user_session = get_user_session(user.id)
        user_session.sum += 1
        sum_q = user_session.sum
        right = user_session.right
        # Кнопки для выбора тематики следующего вопроса.
        await send_text_buttons(update, context, answer,
                                {'quiz_prog': 'Программирование на языке Python',
                                 'quiz_math': 'Математические теории',
                                 'quiz_biology': 'Биология',
                                 'quiz_more': 'Повтор последней темы'})
        # Вывод счётчиков в окно бота.
        await send_text(update, context, f'Количество вопросов: {sum_q}')
        await send_text(update, context, f'Количество првильных ответов: {right}')

# Создаём метод для обработки действия на нажатие кнопок.
async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ожидаем нажатия кнопки.
    await update.callback_query.answer()
    # Получаем "значение" нажатой кнопки.
    callb = update.callback_query.data
    if callb == 'quiz_prog':
        # Делаем запрос к ChatGPT с текстом 'quiz_prog', чтобы получить вопрос по заданной теме.
        question = await chat_gpt.add_message('quiz_prog')
        # Получаем 'ответ' ChatGPT и направляем его в telegram бот.
        await send_text(update, context, question)
        # Выводит в телеграм бот строку "Напишите свой ответ..."
        await send_text(update, context, "Напишите свой ответ...")
        # Запрашиваем данные пользователя для установки переменной last_question пользователя.
        user = update.callback_query.from_user
        user_session = get_user_session(user.id)
        user_session.last_question = 'quiz_prog'
    elif callb == "quiz_math":
        # Делаем запрос к ChatGPT с текстом 'quiz_prog', чтобы получить вопрос по заданной теме.
        question = await chat_gpt.add_message('quiz_math')
        # Получаем 'ответ' ChatGPT и направляем его в telegram бот.
        await send_text(update, context, question)
        # Выводит в телеграм бот строку "Напишите свой ответ..."
        await send_text(update, context, "Напишите свой ответ...")
        # Запрашиваем данные пользователя для установки переменной last_question пользователя.
        user = update.callback_query.from_user
        user_session = get_user_session(user.id)
        user_session.last_question = 'quiz_math'
    elif callb == 'quiz_biology':
        # Делаем запрос к ChatGPT с текстом 'quiz_prog', чтобы получить вопрос по заданной теме.
        question = await chat_gpt.add_message('quiz_biology')
        # Получаем 'ответ' ChatGPT и направляем его в telegram бот.
        await send_text(update, context, question)
        # Выводит в телеграм бот строку "Напишите свой ответ..."
        await send_text(update, context, "Напишите свой ответ...")
        # Запрашиваем данные пользователя для установки переменной last_question пользователя.
        user = update.callback_query.from_user
        user_session = get_user_session(user.id)
        user_session.last_question = 'quiz_biology'
    elif callb == 'quiz_more':
        # Загружаем последнюю 'тематику' пользователя.
        user = update.callback_query.from_user
        user_session = get_user_session(user.id)
        # Делаем запрос к ChatGPT с текстом из переменной last_questiion, чтобы получить вопрос по заданной теме.
        question = await chat_gpt.add_message(f'{user_session.last_question}') # Можно ли здесь сделать без этой конструкции с ковычками?
        # Получаем 'ответ' ChatGPT и направляем его в telegram бот.
        await send_text(update, context, question)
        # Выводит в телеграм бот строку "Напишите свой ответ..."
        await send_text(update, context, "Напишите свой ответ...")
    else:
        await exit_to_start(update, context)

# Задание №6. Переводчик.
async def translator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если пользователь отправил команду сообщением.
    if update.message:
        # Получаем данные пользователя (для id)
        user = update.message.from_user
        # Создаём объект UserSession.
        user_session = get_user_session(user.id)
        # Устанавливаем режим диалога TRANS для СonversationHandler в объекте пользовательской сессии.
        user_session.state = TRANS
    # Если пользователь отправил команду кнопкой.
    else:
        # Получаем данные пользователя (для id)
        user = update.callback_query.from_user
        # Создаём объект UserSession.
        user_session = get_user_session(user.id)
        # Устанавливаем режим диалога TRANS для СonversationHandler в объекте пользовательской сессии.
        user_session.state = TRANS
    # Создаём переменную text с текстом из файла translator папки messages
    text = load_message('translator')
    # Ожидаем загрузки картинки translator из папки images в бот
    await send_image(update,context,'translator')
    # Создаём кнопки для взаимодействия с пользователем
    await send_text_buttons(update, context, text, {'trans_eng': 'Английский', 'trans_deu': 'Немецкий', 'trans_jap': 'Японский', 'trans_fra': 'Французский'})
    # Возвращаем значение "режима" диалога для СonversationHandler.
    return user_session.state  # Не работает, если ставлю здесь TRANS. Почему?

# Создаём метод для общения с ChatGPT
async def trans_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ожидаем загрузки текста переменной text в бот. Присваиваем значение, чтобы затем можно было изменить.
    text = update.message.text
    # Делаем запрос к ChatGPT с текстом из телеграм бота (одновременной создаём переменную answer с ответом)
    answer = await chat_gpt.add_message(text)
    # Кнопки для выбора языка.
    await send_text_buttons(update, context, answer, {'trans_eng': 'Английский', 'trans_deu': 'Немецкий', 'trans_jap': 'Японский', 'trans_fra': 'Французкий'})

# Создаём метод для обработки действия на нажатие кнопок.
async def trans_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ожидаем нажатия кнопки.
    await update.callback_query.answer()
    # Получаем "значение" нажатой кнопки.
    callb = update.callback_query.data
    if callb == 'trans_eng':
        # Создаём переменную promt с текстом из файла trans_eng папки promtpts.
        prompt = load_prompt('trans_eng')
        # Загружаем prompt для ChatGPT, для установки языка перевода.
        chat_gpt.set_prompt(prompt)
        # Выводит в телеграм бот строку "Напишите текст для перевода..."
        await send_text(update, context, "Напишите текст для перевода...")
    elif callb == "trans_deu":
        # Создаём переменную promt с текстом из файла trans_deu папки promtpts.
        prompt = load_prompt('trans_deu')
        # Загружаем prompt для ChatGPT, для установки языка перевода.
        chat_gpt.set_prompt(prompt)
        # Выводит в телеграм бот строку "Напишите текст для перевода..."
        await send_text(update, context, "Напишите текст для перевода...")
    elif callb == 'trans_jap':
        # Создаём переменную promt с текстом из файла trans_jap папки promtpts.
        prompt = load_prompt('trans_jap')
        # Загружаем prompt для ChatGPT, для установки языка перевода.
        chat_gpt.set_prompt(prompt)
        # Выводит в телеграм бот строку "Напишите текст для перевода..."
        await send_text(update, context, "Напишите текст для перевода...")
    elif callb == 'trans_fra':
        # Создаём переменную promt с текстом из файла trans_fra папки promtpts.
        prompt = load_prompt('trans_fra')
        # Загружаем prompt для ChatGPT, для установки языка перевода.
        chat_gpt.set_prompt(prompt)
        # Выводит в телеграм бот строку "Напишите текст для перевода..."
        await send_text(update, context, "Напишите текст для перевода...")
    else:
        await exit_to_start(update, context)

# Создаём класс объекта для хранения состояния клиента бота.
class UserSession:
    # Инициация объекта
    def __init__(self, user_id):
        self.user_id = user_id
        self.state = None
        self.right = None
        self.sum = None
        self.last_question = None
        self.data = {} # Что например здесь можно хранить?

# Сохранение состояния в базе данных.
user_sessions = {}

# Метод для создания пользовательской сессии
def save_user_session(user_session):
    user_sessions[user_session.user_id] = user_session

# Метод для получения объекта пользовательской сессии
def get_user_session(user_id):
# Возвращаем объект "UserSession"
    return user_sessions.get(user_id)

# Метод для сброса параметров пользовательской сессии.
async def exit_to_start(update, context):
    # Если пользователь отправил команду сообщением.
    if update.message:
        user = update.message.from_user
        user_session = get_user_session(user.id)
        # Если пользовательская сессия существует.
        if user_session:
            user_session.state = START
            user_session.right = None
            user_session.sum = None
            user_session.last_question = None
            await update.message.reply_text('Вы вышли. Введите команду /start для справки.')
            return user_session.state
    # Если пользователь отправил команду кнопкой.
    if update.callback_query:
        user = update.callback_query.from_user
        user_session = get_user_session(user.id)
        # Если пользовательская сессия существует.
        if user_session:
            user_session.state = START
            user_session.right = None
            user_session.sum = None
            user_session.last_question = None
            await send_text(update, context, 'Вы вышли. Введите команду /start для справки.')
            return user_session.state

# "Основной" метод.
def main() -> None:

    # Создаём приложение телеграм бота.
    app = ApplicationBuilder().token("8069115680:AAEJhGxyPRKUdy7Jpq2lLIKcCZDyX06oxj0").build()

    # Создаём объект-обработчик СonversationHandler с соответствующими статусами.
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [CommandHandler("random", random), CommandHandler("gpt", ch_gpt), CommandHandler("talk", talk), CommandHandler("quiz", quiz), CommandHandler("trans", translator), MessageHandler(filters.TEXT, start)],
            RANDOM: [CommandHandler("start", start), CommandHandler("random", random), CommandHandler("gpt", ch_gpt), CommandHandler("talk", talk), CommandHandler("quiz", quiz), CommandHandler("trans", translator)],
            GPT: [CommandHandler("start", start), CommandHandler("random", random), CommandHandler("gpt", ch_gpt), CommandHandler("talk", talk), CommandHandler("quiz", quiz), CommandHandler("trans", translator), MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_handler)],
            TALK: [CommandHandler("start", start), CommandHandler("random", random), CommandHandler("gpt", ch_gpt), CommandHandler("talk", talk), CommandHandler("quiz", quiz), CommandHandler("trans", translator), MessageHandler(filters.TEXT & ~filters.COMMAND, talk_handler)],
            QUIZ: [CommandHandler("start", start), CommandHandler("random", random), CommandHandler("gpt", ch_gpt), CommandHandler("talk", talk), CommandHandler("quiz", quiz), CommandHandler("trans", translator), MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_handler)],
            TRANS: [CommandHandler("start", start), CommandHandler("random", random), CommandHandler("gpt", ch_gpt), CommandHandler("talk", talk), CommandHandler("quiz", quiz), CommandHandler("trans", translator), MessageHandler(filters.TEXT & ~filters.COMMAND, trans_handler)],
        },
        fallbacks=[CommandHandler("exit", exit_to_start)],
    )
    # Добавляем обработчик ввода в виде объекта "ConversationHandler".
    app.add_handler(conv_handler)
    # Обработчик кнопки random.
    app.add_handler(CallbackQueryHandler(random_button, pattern='^random.*'))
    # Обработчик кнопок _talk.
    app.add_handler(CallbackQueryHandler(talk_button, pattern='.*talk'))
    # Обработчик кнопок quiz_.
    app.add_handler(CallbackQueryHandler(quiz_button, pattern='^quiz.*'))
    # Обработчик кнопок trans_.
    app.add_handler(CallbackQueryHandler(trans_button, pattern='^trans.*'))
    # Обработчик кнопок по умолчанию.
    app.add_handler(CallbackQueryHandler(default_callback_handler))
    # Команда запуска бота.
    app.run_polling(allowed_updates=Update.ALL_TYPES)

# Создание "связи" с ChatGPT.
chat_gpt = ChatGptService(ChatGPT_TOKEN) #Эта переменная всегда глобальная или её можно куда-нибудь пристроить?

# Создаём переменные "статусов" диалога с пользователем.
START, RANDOM, GPT, TALK, QUIZ, TRANS = range(6) #Эти переменные всегда глобальные или их можно куда-нибудь пристроить?

# Запускаем программу.
main()