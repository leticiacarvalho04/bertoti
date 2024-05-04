import unicodedata
import telebot
from wikipedia import search
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from transformers import pipeline
import requests
import nltk

# Substitua "SEU_TOKEN_AQUI" pelo token do seu bot
bot = telebot.TeleBot('SEU_TOKEN_AQUI')

classifier = pipeline("zero-shot-classification")  # Example model

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Bem-vindo à Cafeteria & Livraria!')
    bot.send_message(message.chat.id, 'Qual livro você está procurando?')
    bot.register_next_step_handler(message, ask_book_details)

def ask_book_details(message):
    book_title = message.text
    bot.send_message(message.chat.id, 'Qual o nome do autor?')
    bot.register_next_step_handler(message, ask_author_details, book_title=book_title)

def ask_author_details(message, book_title):
    author_name = message.text
    search_query = f'{book_title} {author_name}'
    offer_user_choices(message, book_title)

def search_book(message, book_title):
    book_author = message.text

    normalized_title = unicodedata.normalize('NFKD', book_title).encode('ascii', 'ignore').decode('utf-8').lower()
    normalized_author = unicodedata.normalize('NFKD', book_author).encode('ascii', 'ignore').decode('utf-8').lower()
    search_query = f"{normalized_title} title:{normalized_author}"

    try:
        book_info = search(search_query)[0]
    except IndexError:
        bot.send_message(message.chat.id, 'Não encontrei informações sobre esse livro na Wikipedia.')
        return

    book_info_text = f'{book_title}\n\n{book_info}'

    bot.send_message(message.chat.id, book_info_text)

def offer_user_choices(message, book_title):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Ler o livro'))
    keyboard.add(KeyboardButton('Fazer um pedido'))
    keyboard.add(KeyboardButton('Procurar outro livro'))

    bot.send_message(message.chat.id, 'O que você gostaria de fazer?', reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_user_choice, book_title=book_title)

def handle_user_choice(message, book_title):
    intents = ["Ler o livro", "Fazer um pedido", "Procurar outro livro"]
    choice = message.text
    predictions = classifier(choice, intents)
    predicted_intent = predictions['labels'][predictions['scores'].index(max(predictions['scores']))]

    if predicted_intent == 'Ler o livro':
        encoded_title = book_title.replace(" ", "%20")
        bot.send_message(message.chat.id, f'https://pt.z-library.se/s/{encoded_title}')
        bot.send_message(message.chat.id, 'Deseja ler outro livro?')
        if message.text.lower() == 'sim':
            bot.send_message(message.chat.id, 'Qual livro você está procurando?')
            bot.register_next_step_handler(message, ask_book_details)
        else:
            bot.send_message(message.chat.id, 'Obrigado por usar o nosso serviço!')
    elif predicted_intent == 'Fazer um pedido':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton('Café'))
        keyboard.add(KeyboardButton('Bolo'))
        keyboard.add(KeyboardButton('Sanduíche'))
        bot.send_message(message.chat.id, 'Escolha seu pedido:', reply_markup=keyboard)
        bot.register_next_step_handler(message, handle_order)
    elif predicted_intent == 'Procurar outro livro':
        bot.send_message(message.chat.id, 'Qual livro você está procurando?')
        bot.register_next_step_handler(message, ask_book_details)

def handle_order(message):
    order = message.text
    if order == 'Café':
        bot.send_message(message.chat.id, 'Você pediu um Café. Será entregue em breve.')
        bot.send_message(message.chat.id, 'Deseja fazer outro pedido?')
        if(message.text.lower() == 'sim'):
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton('Café'))
            keyboard.add(KeyboardButton('Bolo'))
            keyboard.add(KeyboardButton('Sanduíche'))
            bot.send_message(message.chat.id, 'Escolha seu pedido:', reply_markup=keyboard)
            bot.register_next_step_handler(message, handle_order)
        else:
            bot.send_message(message.chat.id, 'Obrigado por usar o nosso serviço!')
    elif order == 'Bolo':
        bot.send_message(message.chat.id, 'Você pediu um Bolo. Será entregue em breve.')
        if(message.text.lower() == 'sim'):
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton('Café'))
            keyboard.add(KeyboardButton('Bolo'))
            keyboard.add(KeyboardButton('Sanduíche'))
            bot.send_message(message.chat.id, 'Escolha seu pedido:', reply_markup=keyboard)
            bot.register_next_step_handler(message, handle_order)
        else:
            bot.send_message(message.chat.id, 'Obrigado por usar o nosso serviço!')
    elif order == 'Sanduíche':
        bot.send_message(message.chat.id, 'Você pediu um Sanduíche. Será entregue em breve.')
        if(message.text.lower() == 'sim'):
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton('Café'))
            keyboard.add(KeyboardButton('Bolo'))
            keyboard.add(KeyboardButton('Sanduíche'))
            bot.send_message(message.chat.id, 'Escolha seu pedido:', reply_markup=keyboard)
            bot.register_next_step_handler(message, handle_order)
        else:
            bot.send_message(message.chat.id, 'Obrigado por usar o nosso serviço!')
    else:
        bot.send_message(message.chat.id, 'Não reconheço este pedido. Por favor, escolha um item do menu.')

# Inicie o bot.
bot.polling()