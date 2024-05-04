import telebot
from wikipedia import search
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Substitua "SEU_TOKEN_AQUI" pelo token do seu bot
bot = telebot.TeleBot('SEU_TOKE_AQUI')

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
    try:
        book_info = search(f'{book_title} {author_name}')[:1][0]
    except IndexError:
        bot.send_message(message.chat.id, 'Não encontrei informações na Wikipedia.')
        return

    bot.send_message(message.chat.id, f'**{book_title} - {author_name}**\n\n{book_info}')
    offer_user_choices(message)

def offer_user_choices(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Ler o livro'))
    keyboard.add(KeyboardButton('Fazer um pedido'))
    keyboard.add(KeyboardButton('Falar com o atendente'))
    bot.send_message(message.chat.id, 'O que você gostaria de fazer?', reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_user_choice)

def handle_user_choice(message):
    choice = message.text

    if choice == 'Ler o livro':
            bot.send_message(message.chat.id, 'https://pt.z-library.se/{book_title}') 
    elif choice == 'Fazer um pedido':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton('Café'))
        keyboard.add(KeyboardButton('Bolo'))
        keyboard.add(KeyboardButton('Sanduíche'))
        bot.send_message(message.chat.id, 'Escolha seu pedido:', reply_markup=keyboard)
    elif choice == 'Falar com o atendente':
        bot.send_message(message.chat.id, 'Olá! Como posso ajudá-lo?')

# Inicie o bot.
bot.polling()
