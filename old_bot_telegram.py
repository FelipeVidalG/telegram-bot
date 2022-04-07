# -*- coding: utf-8 -*-
from email import message
from genericpath import exists
from operator import contains
from turtle import update
from matplotlib.style import context
import telegram
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import Contact, MessageId, Update
import logging
import sqlite3
        

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
        Ola! Aqui é o robô do Telegram.
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
        reply_markup = telegram.ReplyKeyboardRemove(custom)
        context.bot.send_message(chat_id=update.effective_chat.id, text="""
        Digite um dos números abaixo para escolher uma das opções
        1 --> você escolheu a opção 1
        2 --> você escolheu a opção 2 -- jpeg
        3 --> você escolheu a opção 3 -- video
        4 --> você escolheu a opção 4 -- pdf
        """, reply_markup=reply_markup)
        global numero
        global first_name
        global last_name
        numero = update.message.contact.phone_number
        first_name = update.message.contact.first_name
        last_name = update.message.contact.last_name
        print(f' dentro do mandar opções -> {numero}')
        # print(update.message.contact)
        # print(f"{numero} e {first_name} {last_name}")
        salvar()



# Salvar informações no banco

def salvar():

        banco = sqlite3.connect('banco.db')
        cursor = banco.cursor()
        # cursor.execute("CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, numero text, first_name text, last_name text)")
        print(f' dentro do salvar -> {numero}')
        busca_numeros = cursor.execute("SELECT numero FROM users")
        
        numeros = busca_numeros.fetchall()

        if len(numero) > 0:
                global opcoes_handler
                opcoes_handler = MessageHandler(Filters.text, opcoes)
                dispatcher.add_handler(opcoes_handler)
                dispatcher.remove_handler(tente_novamente_handler)
        print(f' AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA do salvar -> {numero}')

        for i in numeros:
                if i[0] == numero:
                        return False


        if last_name != None:
                cursor.execute("INSERT INTO users VALUES(NULL, '"+ numero + "','"+ first_name + "','"+ last_name +  "')")
        else:
                cursor.execute("INSERT INTO users VALUES(NULL, '"+ numero + "','"+ first_name + "','"+ 'VAZIO' +  "')")


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

print(f' fora -> {numero}')

              

updater.start_polling()