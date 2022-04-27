# -*- coding: utf-8 -*-
from matplotlib import offsetbox
import telegram
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import Contact, MessageId, Update
import logging
import mysql.connector
import time


# inicialização e configuração do bot
updater = Updater(token="5180663220:AAGRZL-gErS01fkfIU0zoRmlCQxaoFLMvV4")
dispatcher = updater.dispatcher

bot = telegram.Bot("5180663220:AAGRZL-gErS01fkfIU0zoRmlCQxaoFLMvV4")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)  # mostrará os erros

numero = ''
sequencia = -1

global opcoes_handler

# opcoes_handler = ''

# responde o command messages /

# solicita contato para o user caso seja a primeira conversa e começa robô
def start(update: Update, context: CallbackContext):
        dispatcher.remove_handler(start_handler2)
        global chat_id
        chat_id = str(update.message.chat_id)

        global sequencia
        sequencia = -1

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
                        # atendimento()
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

start_handler2 = MessageHandler(Filters.text, start)
dispatcher.add_handler(start_handler2)

# Recebe o contato do usuário e manda as opções do menu
def mandar_opcoes(update: Update, context: CallbackContext):
        # atendimento()
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


# Salva as informações no banco de dados

          # busca no banco de dados de usuários
        busca_numeros = cursor.execute("SELECT * FROM tbcontatos")
        numeros = cursor.fetchall()
        # dispatcher.remove_handler(mandar_opcoes_handler)
        dispatcher.add_handler(opcoes_handler)
        dispatcher.remove_handler(tente_novamente_handler)
       
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


# Resposta das opções do menu
def opcoes(update: Update, context: CallbackContext):
        global sequencia
        sequencia += 1
        print(sequencia)
        msg_recebida = update.message.text


        banco = mysql.connector.connect(host='192.168.10.82',database='saw_teste',user='root',password='rapadura')
        cursor = banco.cursor(buffered=True)



        buscar_nome = cursor.execute(f'SELECT nome FROM tbcontatos WHERE chatid = {chat_id}')
        nomes = cursor.fetchall()
        nome = nomes[0][0]

        buscar_numero = cursor.execute(f'SELECT numero FROM tbcontatos WHERE chatid = {chat_id}')
        numeros = cursor.fetchall()
        numero = numeros[0][0]
 
    
        busca_atendimento = cursor.execute(f"SELECT id FROM tbatendimento WHERE numero = '{numero}' AND canal = 3 AND situacao IN('T', 'A') ")
        atendimentos = cursor.fetchall()

        if atendimentos == []:
                cursor.execute(f"SELECT id FROM tbatendimento WHERE numero = {numero}")
                lista_id = cursor.fetchall()
                if lista_id == []:
                        novo_id = 1
                        cursor.execute(f"INSERT INTO tbatendimento (id,situacao,numero,dt_atend,hr_atend,nome,canal,dt_fim) VALUES('{novo_id}','A',{numero},NOW(),NOW(),'{nome}','3',NOW())")
                        cursor.execute(f"INSERT INTO tbmsgatendimento (id,seq,numero,msg,dt_msg,hr_msg,canal) VALUES('{novo_id}','{sequencia}','{numero}','{msg_recebida}',NOW(),NOW(),'3')") 
                else:
                        novo_id = lista_id[-1][0] + 1
                        cursor.execute(f"INSERT INTO tbatendimento (id,situacao,numero,dt_atend,hr_atend,nome,canal,dt_fim) VALUES('{novo_id}','A',{numero},NOW(),NOW(),'{nome}','3',NOW())")
                        cursor.execute(f"INSERT INTO tbmsgatendimento (id,seq,numero,msg,dt_msg,hr_msg,canal) VALUES('{novo_id}','{sequencia}','{numero}','{msg_recebida}',NOW(),NOW(),'3')")

        else:
                print('ATENDIMENTO EM ABERTO!')
                novo_id=atendimentos[0][0]
                cursor.execute(f"INSERT INTO tbmsgatendimento (id,seq,numero,msg,dt_msg,hr_msg,canal,nome_chat) VALUES('{novo_id}','{sequencia}','{numero}','{msg_recebida}',NOW(),NOW(),'3','{nome}')")
                print(sequencia)

        # print(novo_id)
                
        banco.commit()

        # nova estrutura de opções abaixo

        buscar_opcoes = cursor.execute('SELECT id FROM tbmenu')
        opcoes_id = cursor.fetchall()
        
# Verifica opção escolhida e joga a resposta para o usuário, se for inválida retorna o menu novamente.
        for x in opcoes_id:
                if msg_recebida == str(x[0]):
                        try:
                                cursor.execute(f"SELECT descricao FROM tbrespostasautomaticas WHERE id_menu = {msg_recebida}")
                                resposta = cursor.fetchall()
                                resposta = resposta[0][0]
                                cursor.execute(f"SELECT acao FROM tbrespostasautomaticas WHERE id_menu = {msg_recebida}")
                                acao = cursor.fetchall()
                                acao = acao[0][0]
                                print(type(acao))
                                context.bot.send_message(chat_id=update.effective_chat.id,text=f"{resposta}")
                                if acao == '1':
                                        context.bot.send_message(chat_id=update.effective_chat.id,text=f"{menu}")
                                elif acao == '9':
                                        cursor.execute(f"UPDATE `tbatendimento` SET `situacao` = 'F' WHERE `situacao` = 'A' AND `canal` = '3' AND `numero` = '{numero}'")
                                        context.bot.send_message(chat_id=update.effective_chat.id,text=f"Atendimento encerrado!")     
                                        dispatcher.remove_handler(opcoes_handler)
                                        dispatcher.remove_handler(tente_novamente_handler)
                                        dispatcher.add_handler(start_handler2)
                                        banco.commit()

                                return False
#                                 
# context.bot.send_message(chat_id=update.effective_chat.id,text=f"""Deseja encerrar o atendimento?
# 10- SIM
# 11- NAO""")
                        except:
                                cursor.execute(f'SELECT departamento FROM tbdepartamentos WHERE id_menu = {msg_recebida}')
                                resposta = cursor.fetchall()
                                resposta = resposta[0][0]
                                texto = "Você será redirecionado para o departamento: "
                                context.bot.send_message(chat_id=update.effective_chat.id,text=f"{texto} {resposta}")

                                return False

        if msg_recebida == '10':
                cursor.execute(f"UPDATE `tbatendimento` SET `situacao` = 'F' WHERE `situacao` = 'A' AND `canal` = '3' AND `numero` = '{numero}'")
                context.bot.send_message(chat_id=update.effective_chat.id,text=f"Atendimento encerrado!")     
                dispatcher.remove_handler(opcoes_handler)
                dispatcher.remove_handler(tente_novamente_handler)
                dispatcher.add_handler(start_handler2)
                banco.commit()

        else:
                context.bot.send_message(chat_id=update.effective_chat.id,text=f"Opção inválida selecione outra opção:\n{menu}")


# suporte manda mensagem para o usuario
def mandar_msg_user():
        banco = mysql.connector.connect(host='192.168.10.82',database='saw_teste',user='root',password='rapadura')
        cursor = banco.cursor(buffered=True)

        cursor.execute(f"SELECT numero FROM tbmsgatendimento WHERE situacao = 'E'")
        numeros1 = cursor.fetchall()
        print(numeros1)

        if numeros1 == []:
                numeros1 = False


        while numeros1:
                for num in numeros1:
                        time.sleep(2)
                        try:
                                print('entrou2')
                                cursor.execute(f"SELECT chatid FROM tbcontatos WHERE numero={num[0]}")
                                chat_id = cursor.fetchall()
                                chat_id = chat_id[0][0]
                                cursor.execute(f"SELECT msg FROM tbmsgatendimento WHERE numero={num[0]} AND situacao = 'E'")
                                msg_atendimento = cursor.fetchall()
                                msg_atendimento = msg_atendimento[0][0]
                                bot.send_message(chat_id=chat_id,text=msg_atendimento)

                                print(num[0])
                                print(msg_atendimento)

                                cursor.execute(f"UPDATE tbmsgatendimento SET situacao = 'N' WHERE situacao = 'E' AND numero = {num[0]} AND msg = '{msg_atendimento}'")
                                banco.commit()
                                print('chegou')
                        except:
                                print('alguns não temos chat id')


# Caso usuário não envie contato entra nessa função
def tente_novamente(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text="""
        Por favor, envie seu contato para continuar. \nCaso estiver usando o telegram web clique no ícone demonstrado a seguir.
        """)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('files/icone_contato.png', 'rb'))


tente_novamente_handler = MessageHandler(Filters.text, tente_novamente)

opcoes_handler = MessageHandler(Filters.text, opcoes)

updater.start_polling()


# Mandar mensagens enviadas pelo suporte para o user
while (True):

        time.sleep(1)
        banco = mysql.connector.connect(host='192.168.10.82',database='saw_teste',user='root',password='rapadura')
        cursor = banco.cursor(buffered=True)    
        # pegando números com situação E
        cursor.execute(f"SELECT numero FROM tbmsgatendimento WHERE situacao='E'")
        numeros123 = cursor.fetchall()

        # print(numeros123)

        # removendo a repetição do mesmo número
        def remove_repetidos(lista):
                l = []
                for i in lista:
                        if i not in l:
                                l.append(i)
                l.sort()
                return l

        numeros123 = remove_repetidos(numeros123)

        try:
                for i in numeros123:
                        cursor.execute(f"SELECT chatid FROM tbcontatos WHERE numero = {i[0]}")
                        chatid = cursor.fetchall()
                        chatid = chatid[0][0]

                        cursor.execute(f"SELECT numero FROM tbcontatos WHERE chatid={chatid}")
                        numeros_com_chatid = cursor.fetchall()
                        numeros_com_chatid = numeros_com_chatid[0][0]


                cursor.execute(f"SELECT msg FROM tbmsgatendimento WHERE numero = {i[0]} and situacao = 'E'")
                msg = cursor.fetchall()
                
                # print(msg)
                # print(chatid)

                try:
                        for x in msg:
                                bot.send_message(chat_id=chatid,text=x[0])
                                cursor.execute(f"UPDATE tbmsgatendimento set situacao='N' WHERE situacao='E' AND numero={numeros_com_chatid}")
                                banco.commit()
                except:
                        pass
        except:
                # print('sem mensagens novas para enviar')
                pass