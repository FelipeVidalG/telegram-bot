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
        banco = mysql.connector.connect(host='192.168.10.82',database='saw_teste',user='root',password='rapadura')
        cursor = banco.cursor(buffered=True)
        
        busca_opcoes = cursor.execute("SELECT * FROM tbcontatos")
        opcoes = cursor.fetchall()

        busca_menu = cursor.execute("SELECT * FROM tbmenu ORDER BY sequencia")
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
                if str(i[1])==chat_id:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=menu)  
                        atendimento()
                        global mandar_opcoes_handler
                        # mandar_opcoes_handler = MessageHandler(Filters.text, mandar_opcoes)
                        dispatcher.add_handler(opcoes_handler)
                        # dispatcher.remove_handler(tente_novamente_handler)
                        return False
        
        
        # caso seja a primeira vez do usuário solicita o contato
        mandar_opcoes_handler = MessageHandler(Filters.contact, mandar_opcoes)
        context.bot.send_message(chat_id=update.effective_chat.id, text="""
        Ola! Aqui é o robô do Telegram.
        Envie seu contato para podemos prosseguir:
        """,reply_markup=reply_markup)  
        dispatcher.add_handler(mandar_opcoes_handler)
        dispatcher.add_handler(tente_novamente_handler)


# executa a função
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)



# Recebe o contato do usuário e manda as opções do menu
def mandar_opcoes(update: Update, context: CallbackContext):
        atendimento()
        # chat_id=update.effective_chat.id -> localização da mensagem (os chats com updates)
        # update.message.text --> ultimo mensagem do chat 
        # dispatcher.remove_handler(start_handler)

        # remove o handler de tente novamente
        dispatcher.remove_handler(tente_novamente_handler)

        # conexao com o banco para fazer buscas
        banco = mysql.connector.connect(host='192.168.10.82',database='saw_teste',user='root',password='rapadura')
        cursor = banco.cursor(buffered=True)
        busca_opcoes = cursor.execute("SELECT * FROM tbmenu ORDER BY sequencia")
        opcoes = cursor.fetchall()

        # gera menu de opções através do banco
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
        global nome
        try:
                numero = update.message.contact.phone_number
                first_name = update.message.contact.first_name
                last_name = update.message.contact.last_name
                nome = f'{first_name} {last_name}'
        except:
                print('erro')
                pass
        # print(update.message.contact)
        # print(f"{numero} e {first_name} {last_name}")
        salvar()



# Salva as informações no banco de dados

def salvar():

        # conexão com o banco
        banco = mysql.connector.connect(host='192.168.10.82',database='saw_teste',user='root',password='rapadura')
        cursor = banco.cursor(buffered=True)
        # cursor.execute("CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, numero text, first_name text, last_name text)")
        
        # busca no banco de dados de usuários
        busca_numeros = cursor.execute("SELECT * FROM tbcontatos")
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
                        cursor.execute(f"INSERT INTO tbcontatos (numero,chatid,nome) VALUES('{numero}','{chat_id}','{nome}')")
                else:
                        nome = first_name
                        cursor.execute(f"INSERT INTO tbcontatos (numero,chatid,nome) VALUES('{numero}','{chat_id}','{nome}')")
        except:
                print('erro banco')
                pass


        banco.commit()

        
def atendimento():
         # conexao com o banco para fazer buscas
        banco = mysql.connector.connect(host='192.168.10.82',database='saw_teste',user='root',password='rapadura')
        cursor = banco.cursor(buffered=True)

        global nome
        buscar_nome = cursor.execute(f'SELECT nome FROM tbcontatos WHERE chatid = {chat_id}')
        nomes = cursor.fetchall()
        nome = nomes[0][0]

        global numero
        buscar_numero = cursor.execute(f'SELECT numero FROM tbcontatos WHERE chatid = {chat_id}')
        numeros = cursor.fetchall()
        numero = numeros[0][0]
    
        busca_atendimento = cursor.execute(f"SELECT id FROM tbatendimento WHERE numero = '{numero}' AND canal = 3 AND situacao IN('T', 'A') ")
        atendimentos = cursor.fetchall()

        global novo_id

        if atendimentos == []:
                cursor.execute(f"SELECT id FROM tbatendimento WHERE numero = {numero}")
                lista_id = cursor.fetchall()
                if lista_id == []:
                        novo_id = 1
                        cursor.execute(f"INSERT INTO tbatendimento (id,situacao,numero,nome,canal) VALUES('{novo_id}','A',{numero},'{nome}','3')")
                else:
                        novo_id = lista_id[-1][0] + 1
                        cursor.execute(f"INSERT INTO tbatendimento (id,situacao,numero,nome,canal) VALUES('{novo_id}','A','{numero}','{nome}','3')")
        else:
                print('ATENDIMENTO EM ABERTO!')
                
        banco.commit()
                

# Resposta das opções do menu
def opcoes(update: Update, context: CallbackContext):
        global msg_recebida
        msg_recebida = update.message.text
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
                # salvar_msg()

def salvar_msg():
        banco = mysql.connector.connect(host='192.168.10.82',database='saw_teste',user='root',password='rapadura')
        cursor = banco.cursor(buffered=True)
        print(msg_recebida, novo_id)
        cursor.execute(f"INSERT INTO tbmsgatendimento (id,numero,msg,canal,nome_chat) VALUES('{novo_id}','{numero}','{msg_recebida}','3','{nome}')")
        banco.commit()

# Caso usuário não envie contato entra nessa função
def tente_novamente(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text="""
        Por favor, envie seu contato para continuar. \nCaso estiver usando o telegram web clique no ícone demonstrado a seguir.
        """)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('files/icone_contato.png', 'rb'))
        

tente_novamente_handler = MessageHandler(Filters.text, tente_novamente)

opcoes_handler = MessageHandler(Filters.text, opcoes)


              

updater.start_polling()