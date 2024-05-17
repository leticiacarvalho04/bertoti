import telebot
from wikipedia import search
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from transformers import pipeline

# Substitua "SEU_TOKEN_AQUI" pelo token do seu bot
bot = telebot.TeleBot('6047718024:AAGKNKb2xF0r-Glmvu1wPlPFwVKO9H6F_c4')

classifier = pipeline("zero-shot-classification")

popular_books = []

def get_popular_books():
    url = "https://www.googleapis.com/books/v1/volumes?q=subject:fiction&orderBy=newest&maxResults=5"
    response = requests.get(url)
    data = response.json()
    items = data.get('items', [])
    popular_books = []
    for item in items:
        volume_info = item.get('volumeInfo', {})
        book_title = volume_info.get('title', 'Desconhecido')
        authors = volume_info.get('authors', ['Desconhecido'])
        authors_str = ', '.join(authors)
        suggestion = {'title': book_title, 'authors': authors_str}
        popular_books.append(suggestion)
    return popular_books

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
    global popular_books
    popular_books = get_popular_books()
    choices = ["Escolher bebidas", "Pedir um livro", "Pedir uma recomendação de livro"]
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for choice in choices:
        keyboard.add(KeyboardButton(choice))
    
    bot.send_message(message.chat.id, 'Bem-vindo à Cafeteria & Livraria!')
    bot.send_message(message.chat.id, 'Como posso ajudar você hoje?', reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_user_input)

def handle_user_input(message):
    global popular_books
    user_input = message.text
    
    intents = ["Escolher bebidas", "Pedir um livro", "Pedir uma recomendação de livro"]
    classification_result = classifier(user_input, intents)
    detected_intent = classification_result['labels'][0]

    if detected_intent in ['Pedir um livro', 'Pedir uma recomendação de livro']:
        if 'recomendação' in user_input.lower():
            detected_intent = 'Pedir uma recomendação de livro'
        else:
            detected_intent = 'Pedir um livro'
    
    if detected_intent == 'Pedir um livro':
        bot.send_message(message.chat.id, 'Qual livro você está procurando?')
        bot.register_next_step_handler(message, ask_book_details)
    elif detected_intent == 'Escolher bebidas':
        offer_drinks(message)
    elif detected_intent == 'Pedir uma recomendação de livro':
        popular_books = get_popular_books()
        bot.send_message(message.chat.id, 'Aqui estão alguns livros populares:')
        for i, book in enumerate(popular_books, start=1):
            bot.send_message(message.chat.id, f"{i}. {book['title']} - {book['authors']}")
        bot.send_message(message.chat.id, 'Qual desses livros você gostaria de pedir? Por favor, forneça o número correspondente.')
        bot.register_next_step_handler(message, handle_book_choice)
    else:
        bot.send_message(message.chat.id, 'Desculpe, não entendi sua solicitação.')

def handle_book_choice(message):
    global popular_books
    book_index = int(message.text) - 1
    if 0 <= book_index < len(popular_books):
        chosen_book = popular_books[book_index]
        bot.send_message(message.chat.id, f"Você escolheu '{chosen_book['title']}' de {chosen_book['authors']}.")
        offer_user_choices(message, chosen_book['title'], chosen_book['authors'])
    else:
        bot.send_message(message.chat.id, 'Opção inválida. Por favor, escolha um número correspondente a um dos livros recomendados.')
        bot.register_next_step_handler(message, handle_book_choice)
def ask_book_details(message):
    book_title = message.text
    bot.send_message(message.chat.id, 'Qual o nome do autor?')
    bot.register_next_step_handler(message, ask_author_details, book_title=book_title)

def ask_author_details(message, book_title):
    author_name = message.text
    offer_user_choices(message, book_title, author_name)  

def offer_user_choices(message, book_title, author_name):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Ler o livro'))
    keyboard.add(KeyboardButton('Fazer um pedido'))
    keyboard.add(KeyboardButton('Procurar outro livro'))

    bot.send_message(message.chat.id, 'O que você gostaria de fazer?', reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_user_choice, book_title=book_title, author_name=author_name)

def handle_user_choice(message, book_title, author_name):
    choice = message.text.lower()

    if 'ler o livro' in choice:
        amazon_search_link = f"https://www.amazon.com/s?k={book_title.replace(' ', '+')}"
        bot.send_message(message.chat.id, f"Você escolheu ler o livro '{book_title}'.")
        bot.send_message(message.chat.id, f'Você pode encontrar mais sobre "{book_title}" na Amazon: {amazon_search_link}')
        bot.send_message(message.chat.id, 'Deseja fazer outro pedido? (Sim/Não)')
        bot.register_next_step_handler(message, handle_next_choice, book_title=book_title, author_name=author_name)
        
    elif 'fazer um pedido' in choice:
        offer_drinks(message)

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

def offer_drinks(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Café'))
    keyboard.add(KeyboardButton('Suco'))
    keyboard.add(KeyboardButton('Chá'))
    bot.send_message(message.chat.id, 'Escolha sua bebida:', reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_drink_order)

def handle_drink_order(message):
    order = message.text.lower()
    if order in ['café', 'suco', 'refrigerante']:
        bot.send_message(message.chat.id, f'Você pediu um {order}. Será entregue em breve.')
        bot.send_message(message.chat.id, 'Deseja fazer outro pedido? (Sim/Não)')
        bot.register_next_step_handler(message, handle_another_order)
    else:
        bot.send_message(message.chat.id, 'Opção inválida. Por favor, escolha uma das opções fornecidas.')

def handle_another_order(message):
    choice = message.text.lower()
    if 'sim' in choice:
        handle_user_input(message)
    else:
        bot.send_message(message.chat.id, 'Obrigado por usar o nosso serviço!')

# Inicie o bot.
bot.polling()