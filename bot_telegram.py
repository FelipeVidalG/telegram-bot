# -*- coding: utf-8 -*-
import telegram
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import Contact, MessageId, Update
import logging
import mysql.connector

# inicialização
updater = Updater(token="5180663220:AAGRZL-gErS01fkfIU0zoRmlCQxaoFLMvV4")
dispatcher = updater.dispatcher

bot = telegram.Bot("5180663220:AAGRZL-gErS01fkfIU0zoRmlCQxaoFLMvV4")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)  # mostrará os erros

numero = ''

global opcoes_handler
opcoes_handler = ''

# responde o command messages /

# solicita contato para o user e começa robô
def start(update: Update, context: CallbackContext):
        global botao
        global custom

        if opcoes_handler != '':
                dispatcher.remove_handler(opcoes_handler)


        
        botao = telegram.KeyboardButton('Mandar contato', request_contact = True)
        custom = [[botao]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom)
        context.bot.send_message(chat_id=update.effective_chat.id, text="""
        Ola! Aqui é o robô da TireShop.
        Envie seu contato para podemos prosseguir:
        """,reply_markup=reply_markup)  
        

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


# pega o contato enviado pelo user
# Toda mensagem retorna True
def mandar_opcoes(update: Update, context: CallbackContext):
        # chat_id=update.effective_chat.id -> localização da mensagem (os chats com updates)
        # update.message.text --> ultimo mensagem do chat 
        # dispatcher.remove_handler(start_handler)
        banco = mysql.connector.connect(host='',database='saw_teste',user='root',password='')
        cursor = banco.cursor(buffered=True)
        busca_opcoes = cursor.execute("SELECT * FROM menu_telegram")
        opcoes = cursor.fetchall()
        menu_for = []
        text = "Digite um dos números abaixo para escolher uma das opções"
        for i in opcoes:
                menu_id = str(i[0])

                menu_desc =  str(i[3])
                
                menu_for = str(menu_for) + f"""\n{menu_desc}"""

        simbolos = ["[", "]"]
        for c in simbolos:
                menu_for = menu_for.replace(c,'')

        menu = f"""Digite um dos números abaixo para escolher uma das opções:
                {menu_for}"""  
#         menu = f"""
#         Digite um dos números abaixo para escolher uma das opções
#         {opcoes[0][0]} {opcoes[0][3]}
#        {opcoes[1][0]} {opcoes[1][3]}
#         {opcoes[2][0]}  {opcoes[2][3]}
#         {opcoes[3][0]}  {opcoes[3][3]}
#         """
      


        reply_markup = telegram.ReplyKeyboardRemove(custom)
        context.bot.send_message(chat_id=update.effective_chat.id, text=menu, reply_markup=reply_markup)
        global numero
        global first_name
        global last_name
        numero = update.message.contact.phone_number
        first_name = update.message.contact.first_name
        last_name = update.message.contact.last_name
        # print(update.message.contact)
        # print(f"{numero} e {first_name} {last_name}")
        salvar()



# Salvar informações no banco

def salvar():

        banco = mysql.connector.connect(host='192.168.10.82',database='saw_teste',user='root',password='rapadura')
        cursor = banco.cursor(buffered=True)
        # cursor.execute("CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, numero text, first_name text, last_name text)")
        busca_numeros = cursor.execute("SELECT numero FROM teste_telegram")
        numeros = cursor.fetchall()

        if len(numero) > 0:
                global opcoes_handler
                opcoes_handler = MessageHandler(Filters.text, opcoes)
                dispatcher.add_handler(opcoes_handler)
                dispatcher.remove_handler(tente_novamente_handler)
        for i in numeros:
                if str(i[0])==numero:
                        return False


        if last_name != None:
                cursor.execute(f"INSERT INTO teste_telegram (numero,first_name,last_name) VALUES('{numero}','{first_name}','{last_name}')")
        else:
                cursor.execute(f"INSERT INTO teste_telegram (numero,first_name,last_name) VALUES('{numero}','{first_name}','VAZIO')")


        banco.commit()

        

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
                 context.bot.send_message(chat_id=update.effective_chat.id,text="""
        Opção não existente, tente novamente
        Digite um dos números abaixo para escolher uma das opções
        1 --> você escolheu a opção 1
        2 --> você escolheu a opção 2
        3 --> você escolheu a opção 3
        4 --> você escolheu a opção 4
        """)

def tente_novamente(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text="""
        Por favor, envie seu contato para continuar. \nCaso estiver usando o telegram web clique no ícone demonstrado a seguir.
        """)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('files/icone_contato.png', 'rb'))
        

tente_novamente_handler = MessageHandler(Filters.text, tente_novamente)
dispatcher.add_handler(tente_novamente_handler)

mandar_opcoes_handler = MessageHandler(Filters.contact, mandar_opcoes)
dispatcher.add_handler(mandar_opcoes_handler)

# opcoes_handler = MessageHandler(Filters.text, opcoes)
# dispatcher.add_handler(opcoes_handler)


              

updater.start_polling()