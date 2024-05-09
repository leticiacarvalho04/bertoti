import unicodedata
import telebot
from wikipedia import search
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests

# Substitua "SEU_TOKEN_AQUI" pelo token do seu bot
bot = telebot.TeleBot('SEU_TOKEN_AQUI')

def get_book_recommendations(title, author):
    query = f"{title}+inauthor:{author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url)
    data = response.json()
    items = data.get('items', [])
    suggestions = []
    for item in items:
        volume_info = item.get('volumeInfo', {})
        book_title = volume_info.get('title', 'Desconhecido')
        authors = volume_info.get('authors', ['Desconhecido'])
        authors_str = ', '.join(authors)
        suggestion = {'title': book_title, 'authors': authors_str}
        suggestions.append(suggestion)
    return suggestions

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
    offer_user_choices(message, book_title, author_name)  

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

def offer_user_choices(message, book_title, author_name):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Ler o livro'))
    keyboard.add(KeyboardButton('Fazer um pedido'))
    keyboard.add(KeyboardButton('Procurar outro livro'))

    bot.send_message(message.chat.id, 'O que você gostaria de fazer?', reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_user_choice, book_title=book_title, author_name=author_name)

def handle_user_choice(message, book_title, author_name,):
    choice = message.text.lower()

    if 'ler o livro' in choice:
        encoded_title = book_title.replace(" ", "%20")
        bot.send_message(message.chat.id, f'https://pt.z-library.se/s/{encoded_title}')
        bot.send_message(message.chat.id, 'Deseja fazer outro pedido? (Sim/Não)')
        bot.register_next_step_handler(message, handle_next_choice, book_title=book_title, author_name=author_name)
        
    elif 'fazer um pedido' in choice:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton('Café'))
        keyboard.add(KeyboardButton('Bolo'))
        keyboard.add(KeyboardButton('Sanduíche'))
        bot.send_message(message.chat.id, 'Escolha seu pedido:', reply_markup=keyboard)
        bot.register_next_step_handler(message, handle_order)
    elif 'procurar outro livro' in choice:
        bot.send_message(message.chat.id, 'Procurando por sugestões de livros do mesmo gênero...')
        genre_suggestions = get_book_recommendations(book_title, author_name)

        if genre_suggestions:
            bot.send_message(message.chat.id, 'Aqui estão algumas sugestões de livros do mesmo gênero:')
            for suggestion in genre_suggestions:
                bot.send_message(message.chat.id, f"{suggestion['title']} - {suggestion['authors']}")
        else:
            bot.send_message(message.chat.id, 'Não foram encontradas sugestões de livros do mesmo gênero.')

        bot.send_message(message.chat.id, 'Qual livro você está procurando?')
        bot.register_next_step_handler(message, ask_book_details)

def handle_next_choice(message, book_title, author_name):
    choice = message.text.lower()

    if 'sim' in choice:
        offer_user_choices(message, book_title, author_name)
    else:
        bot.send_message(message.chat.id, 'Obrigado por usar o nosso serviço!')

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
