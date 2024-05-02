import telebot
import wikipediaapi

API_TOKEN = 'SEU TOKEN AQUI'
bot = telebot.TeleBot(API_TOKEN)

wiki_wiki = wikipediaapi.Wikipedia(
    language='pt',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent='MeuBot/1.0 (https://github.com/seu_usuario/seu_repositorio)'
)

chat_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bem-vindo ao Bot da Wikipedia! Digite /search seguido do termo que deseja pesquisar.")

@bot.message_handler(commands=['search'])
def search_wikipedia(message):
    search_query = message.text.split('/search ', 1)[1]
    try:
        page = wiki_wiki.page(search_query)
        if page.exists():
            result = page.text
            chat_states[message.chat.id] = {'query': search_query, 'result': result}
            bot.reply_to(message, "Texto encontrado:\n" + result)
            bot.reply_to(message, "Agora, digite /keyword seguido da palavra-chave para obter mais informações.")
        else:
            bot.reply_to(message, "Nenhum resultado encontrado para esta pesquisa.")
    except Exception as e:
        print(e)
        bot.reply_to(message, "Ocorreu um erro ao processar sua pesquisa.")

@bot.message_handler(commands=['keyword'])
def ask_keyword(message):
    chat_id = message.chat.id
    if chat_id in chat_states:
        bot.reply_to(message, "Por favor, digite a palavra-chave para buscar no texto.")
    else:
        bot.reply_to(message, "Não há resultados anteriores para mostrar. Por favor, faça uma nova pesquisa usando /search.")

@bot.message_handler(func=lambda message: True)
def get_info_by_keyword(message):
    chat_id = message.chat.id
    if chat_id in chat_states:
        search_query = chat_states[chat_id]['query']
        result = chat_states[chat_id]['result']
        keyword = message.text
        try:
            snippet = ""
            for line in result.split('\n'):
                if keyword.lower() in line.lower():
                    snippet += line + "\n"
            if snippet:
                bot.reply_to(message, "Trecho encontrado com a palavra-chave '{}':\n{}".format(keyword, snippet))
            else:
                bot.reply_to(message, "Nenhuma informação encontrada com a palavra-chave '{}'.".format(keyword))
        except Exception as e:
            print(e)
            bot.reply_to(message, "Ocorreu um erro ao buscar a palavra-chave.")
    else:
        bot.reply_to(message, "Não há resultados anteriores para mostrar. Por favor, faça uma nova pesquisa usando /search.")

bot.polling()