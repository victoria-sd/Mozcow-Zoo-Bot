import telebot
import yagmail
from telebot import types

from animals_discription import animals_info
from data import TOKEN, BOT_EMAIL_ADDRESS, BOT_EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
from questions import questions

bot = telebot.TeleBot(TOKEN)
user_quiz_results = {}
RECIPIENT_EMAIL = "sapojnikovavika7@gmail.com" #mail сотрудника зоопарка (куда отправлять)

@bot.message_handler(commands=['start', ]) #приветственное письмо и копка для запуска викторины
def start(message: telebot.types.Message):
    text = (
        f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в мир Московского зоопарка! 🦁\n\n"
        "Я твой персональный помощник в удивительном мире наших обитателей. Готов отправиться в увлекательное путешествие и узнать, какое животное станет твоим тотемным спутником? ✨\n\n"
        "Пройди мою короткую и увлекательную викторину, ответив на несколько интересных вопросов. По результатам ты узнаешь свое тотемное животное, которое будет сопровождать тебя в этом приключении! 🐾\n\n"
        "Готов найти своего тотемного друга?\n\n"
        "Нажми кнопку ниже, чтобы начать викторину! 👇"
    )

    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    keyboard_markup.add(types.KeyboardButton("Начать викторину"))

    bot.send_message(message.chat.id, text, reply_markup=keyboard_markup)
    bot.send_message(
        message.chat.id,
        "Если хочешь узнать всё о наших возможностях и командах, просто введи /help — и я расскажу тебе обо всех секретах "
        "нашего зоопарка! 🌟"
    )


@bot.message_handler(commands=['help']) #основные комманды бота + ссылки на сайт и тг-канал зоопарка
def send_help(message: telebot.types.Message):
    help_text = (
        "🤖 **Основные команды бота Московского зоопарка:**\n\n"
        "/start - Начало викторины. Узнай свое тотемное животное!\n"
        "/contacts - Отправить запрос на обратную связь с сотрудником зоопарка для получения дополнительной информации.\n"
        "/help - Информация о командах бота.\n"
        "/feedback - Оставить обратную связь.\n\n"
        "Информацию о животных можно найти [на сайте зоопарка](https://moscowzoo.ru/animals/) и в [Telegram-канале](https://t.me/Moscowzoo_official).\n"
        "Чтобы узнать больше подробностей о программе «Возьми животное под опеку» перейди по [ссылке](https://moscowzoo.ru/my-zoo/become-a-guardian/)."
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


@bot.message_handler(commands=['feedback'])
def handle_feedback_command(message):
    bot.send_message(message.chat.id, "Пожалуйста, оставьте ваш отзыв о боте и его работе.")
    bot.register_next_step_handler(message, process_feedback)


def process_feedback(message):
    feedback_text = message.text

    with open('feedbacks.txt', 'a', encoding='utf-8') as f:   #cохраняем отзыв в файл
        f.write(f"User`s telegram ID: @{message.from_user.username}, Username: {message.from_user.first_name}\n")
        f.write(f"Отзыв: {feedback_text}\n")
        f.write("-" * 40 + "\n")

    bot.send_message(message.chat.id, "Спасибо за ваш отзыв! Он поможет нам улучшить бота.")

@bot.message_handler(commands=['contacts']) #отправка запроса пользователя сотруднику зоопарка с результатми викторины/статусом прохождения
def handle_contacts(message: telebot.types.Message):
    user_id = message.from_user.id
    user_data = user_quiz_results.get(user_id)

    contact_info_lines = [f"Запрос контакта от пользователя {message.from_user.first_name} (Telegram ID: @{message.from_user.username})"]  #определяем ID тг аккаунта пользователя

    if user_data:
        if user_data.get("status") == "finished": #если викторина завершена, получаем тотемное животное пользователя
            quiz_result = user_data.get("animal", "не определено")
            contact_info_lines.append(f"Тотемное животное: {quiz_result}")
        elif user_data.get("status") == "started":
            contact_info_lines.append("Викторина начата, но не пройдена.")
    else:
        contact_info_lines.append("Викторину еще не начинал.")

    contact_info_string = "\n".join(contact_info_lines)

    try:
        yag = yagmail.SMTP(BOT_EMAIL_ADDRESS, BOT_EMAIL_PASSWORD, host=SMTP_SERVER, port=SMTP_PORT) #для отправки письма инициализируем yagmail

        subject = f"Запрос контакта от пользователя Московского зоопарка"
        body = f"""
        Здравствуйте!

        Поступил запрос на связь от пользователя Telegram:

        {contact_info_string}

        Пожалуйста, свяжитесь с пользователем или ответьте на его вопросы.
        """

        yag.send(to=RECIPIENT_EMAIL, subject=subject, contents=body)
        bot.send_message(message.chat.id, "Ваш запрос успешно отправлен сотруднику зоопарка. Мы свяжемся с вами в ближайшее время.")

    except Exception as e:
        print(f"Ошибка при отправке письма: {e}") #если возникнет ошибка, выйдет в терминале
        bot.send_message(message.chat.id, "К сожалению, произошла ошибка при отправке вашего запроса. Пожалуйста, попробуйте снова позже.")

@bot.message_handler(func=lambda message: message.text in ["Начать викторину", "Попробовать ещё раз?"]) #начало/повтор викторины
def handle_quiz_start_or_restart(message: telebot.types.Message):
    if message.text == "Начать викторину":
        bot.send_message(message.chat.id, "Отлично! Начинаем викторину. Вот твой первый вопрос...")
    elif message.text == "Попробовать ещё раз?":
        bot.send_message(message.chat.id, "Повторная викторина! Вот твой первый вопрос...")

    user_id = message.from_user.id
    user_quiz_results[user_id] = {          #обнуляем или создаем данные пользователя
        "answers": [],  #список ответов
        "current_q": 0,  #индекс текущего вопроса (первый вопрос = 0)
        "status": "started"
    }
    ask_question(message)


def ask_question(message): #вопросы викторины
    user_id = message.from_user.id
    user_data = user_quiz_results.get(user_id)
    if user_data is None: #проверяем начал ли пользователь проходить викторину, если нет, функция завершает работу
        return

    current_q_index = user_data["current_q"]
    if current_q_index >= len(questions): #если все вопросы заданы, вызываем функцию подсчета результатов
        finish_quiz(message)
        return

    q = questions[current_q_index]
    question_text = q["question"]
    answers = q["answers"]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) #создаем клавиатуру с вариантами
    for answer_text, _ in answers:
        markup.add(types.KeyboardButton(answer_text))
    bot.send_message(message.chat.id, question_text, reply_markup=markup)


@bot.message_handler(func=lambda m: True) #обработка ответов
def handle_answer(message):
    user_id = message.from_user.id
    user_data = user_quiz_results.get(user_id)
    if not user_data or user_data.get("status") != "started": #условие проверки того, что пользователь начал викторину
        return

    current_q_index = user_data["current_q"]
    if current_q_index >= len(questions): #условие прекращения фугкции, если уже заданы все вопросы
        return

    selected_text = message.text #получаем ответ пользователя и записываем соответствующий балл в в список ответов пользователя
    answers = questions[current_q_index]["answers"]
    for answer_text, score in answers:
        if answer_text == selected_text:
            user_data["answers"].append(score)
            break
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите один из вариантов.")
        return

    user_data["current_q"] += 1 #переходим к следующему вопросу
    ask_question(message)

def finish_quiz(message): #определяем тоемное животное
    user_id = message.from_user.id
    user_data = user_quiz_results.get(user_id)
    total_score = sum(user_data["answers"])
    if total_score <= 14:
        animal = "Лемур 🦝"
    elif total_score <= 21:
        animal = "Обезьяна 🦍"
    elif total_score <= 28:
        animal = "Черепаха 🐢"
    else:
        animal = "Лев 🦁"

    animal_post_info = animals_info.get(animal) #получаем животное из animals_info, далее его описание и фото
    animal_discription = animal_post_info.get("description")
    animal_image = animal_post_info.get("image")

    user_data["status"] = "finished" #отмечаем статус пользователя как завершивший викторину

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) #создаем кнопку для повторного прохождения
    markup.add(types.KeyboardButton("Попробовать ещё раз?"))

    bot.send_photo(message.chat.id, animal_image, caption=f"🎉 Поздравляем! Ваше тотемное животное — *{animal}*.", parse_mode='Markdown')

    details_text = (
        f"{animal_discription}\n\n"
        "Узнать подробнее о программе можно по [ссылке](https://moscowzoo.ru/my-zoo/become-a-guardian/).\n\n"
        "Спасибо за участие в викторине!\n\n"
        "Хотите пройти викторину еще раз и узнать новое тотемное животное? Нажмите кнопку ниже! 🐾✨"
    )
    bot.send_message(message.chat.id, details_text, reply_markup=markup, parse_mode='Markdown')

bot.polling()