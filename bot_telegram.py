# -*- coding: utf-8 -*-
import telegram
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import Contact, MessageId, Update
import logging
import mysql.connector

# inicialização e configuração do bot
updater = Updater(token="5180663220:AAGRZL-gErS01fkfIU0zoRmlCQxaoFLMvV4")
dispatcher = updater.dispatcher

bot = telegram.Bot("5180663220:AAGRZL-gErS01fkfIU0zoRmlCQxaoFLMvV4")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)  # mostrará os erros

numero = ''

global opcoes_handler
# opcoes_handler = ''

# responde o command messages /

# solicita contato para o user caso seja a primeira conversa e começa robô
def start(update: Update, context: CallbackContext):
        global chat_id
        chat_id = str(update.message.chat_id)
       
        # conexao com o banco para fazer buscas
        banco = mysql.connector.connect(host='',database='saw_teste',user='root',password='')
        cursor = banco.cursor(buffered=True)
        
        busca_opcoes = cursor.execute("SELECT * FROM teste_telegram")
        opcoes = cursor.fetchall()

        busca_menu = cursor.execute("SELECT * FROM menu_telegram ORDER BY sequencia")
        menu_resultado = cursor.fetchall()

        global botao
        global custom
        
        botao = telegram.KeyboardButton('Mandar contato', request_contact = True)
        custom = [[botao]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom)

        if opcoes_handler != '':
                dispatcher.remove_handler(opcoes_handler)


        # busca no banco as opções do menu
        menu_for = []
        for i in menu_resultado:
                menu_desc =  str(i[3])
                menu_for = str(menu_for) + f"""\n{menu_desc}"""

        simbolos = ["[", "]"]
        for c in simbolos:
                menu_for = menu_for.replace(c,'')

        

        global menu
        text = "Digite um dos números abaixo para escolher uma das opções:"
        menu = f"""{text}
                {menu_for}"""  

        # compara todos os chat id do banco de dados com o chat id da conversa atual
        for i in opcoes:
                if str(i[4])==chat_id:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=menu)  
                        global mandar_opcoes_handler
                        # mandar_opcoes_handler = MessageHandler(Filters.text, mandar_opcoes)
                        dispatcher.add_handler(opcoes_handler)
                        # dispatcher.remove_handler(tente_novamente_handler)
                        return False
        
        
        # caso seja a primeira vez do usuário solicita o contato
        mandar_opcoes_handler = MessageHandler(Filters.contact, mandar_opcoes)
        context.bot.send_message(chat_id=update.effective_chat.id, text="""
        Ola! Aqui é o robô da TireShop.
        Envie seu contato para podemos prosseguir:
        """,reply_markup=reply_markup)  
        dispatcher.add_handler(mandar_opcoes_handler)
        dispatcher.add_handler(tente_novamente_handler)


# executa a função
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


# Recebe o contato do usuário e manda as opções do menu
def mandar_opcoes(update: Update, context: CallbackContext):
        # chat_id=update.effective_chat.id -> localização da mensagem (os chats com updates)
        # update.message.text --> ultimo mensagem do chat 
        # dispatcher.remove_handler(start_handler)
        dispatcher.remove_handler(tente_novamente_handler)
        banco = mysql.connector.connect(host='192.168.10.82',database='saw_teste',user='root',password='rapadura')
        cursor = banco.cursor(buffered=True)
        busca_opcoes = cursor.execute("SELECT * FROM menu_telegram ORDER BY sequencia")
        opcoes = cursor.fetchall()
        menu_for = []
        for i in opcoes:
                menu_desc =  str(i[3])
                menu_for = str(menu_for) + f"""\n{menu_desc}"""

        simbolos = ["[", "]"]
        for c in simbolos:
                menu_for = menu_for.replace(c,'')

        

        global menu
        text = "Digite um dos números abaixo para escolher uma das opções:"
        menu = f"""{text}
                {menu_for}"""  


        reply_markup = telegram.ReplyKeyboardRemove(custom)
        context.bot.send_message(chat_id=update.effective_chat.id, text=menu, reply_markup=reply_markup)
        global numero
        global first_name
        global last_name
        try:
                numero = update.message.contact.phone_number
                first_name = update.message.contact.first_name
                last_name = update.message.contact.last_name
        except:
                pass
        # print(update.message.contact)
        # print(f"{numero} e {first_name} {last_name}")
        salvar()



# Salva as informações no banco de dados

def salvar():

        # conexão com o banco
        banco = mysql.connector.connect(host='',database='saw_teste',user='root',password='')
        cursor = banco.cursor(buffered=True)
        # cursor.execute("CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, numero text, first_name text, last_name text)")
        
        # busca no banco de dados de usuários
        busca_numeros = cursor.execute("SELECT numero FROM teste_telegram")
        numeros = cursor.fetchall()
        dispatcher.remove_handler(mandar_opcoes_handler)

        global opcoes_handler
        opcoes_handler = MessageHandler(Filters.text, opcoes)
        dispatcher.add_handler(opcoes_handler)
        # dispatcher.remove_handler(tente_novamente_handler)
       
        # compara o numero atual com os numeros cadastrados no banco de dados
        for i in numeros:
                if str(i[0])==numero:
                        return False

        # caso usuário não esteja cadastrado, cadastra informações no banco
        try:
                if last_name != None:
                        cursor.execute(f"INSERT INTO teste_telegram (numero,first_name,last_name,chat_id) VALUES('{numero}','{first_name}','{last_name}','{chat_id}')")
                else:
                        cursor.execute(f"INSERT INTO teste_telegram (numero,first_name,last_name,chat_id) VALUES('{numero}','{first_name}','VAZIO','{chat_id}')")
        except:
                pass


        banco.commit()

        

# Resposta das opções do menu
def opcoes(update: Update, context: CallbackContext):
        if update.message.text == '1':
                context.bot.send_message(chat_id=update.effective_chat.id, text='você escolheu a opção 1')
        elif update.message.text == '2':
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('files/images.jpg', 'rb'))
        elif update.message.text == '3':
                context.bot.send_video(chat_id=update.effective_chat.id,video=open('files/realshort.mp4', 'rb'), supports_streaming=True)
        elif update.message.text == '4':
                context.bot.send_document(chat_id=update.effective_chat.id, document=open('files/report.pdf', 'rb'))
        else:
                 context.bot.send_message(chat_id=update.effective_chat.id,text=f"""Opção inválida, tente novamente:\n{menu}""")

# Caso usuário não envie contato entra nessa função
def tente_novamente(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text="""
        Por favor, envie seu contato para continuar. \nCaso estiver usando o telegram web clique no ícone demonstrado a seguir.
        """)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('files/icone_contato.png', 'rb'))
        

tente_novamente_handler = MessageHandler(Filters.text, tente_novamente)

opcoes_handler = MessageHandler(Filters.text, opcoes)


              

updater.start_polling()