# -*- coding: utf-8 -*-
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
                                texto = "TESTE: "
                                context.bot.send_message(chat_id=update.effective_chat.id,text=f"{texto} {resposta}")
                                context.bot.send_message(chat_id=update.effective_chat.id,text=f"""Deseja encerrar o atendimento?
                                10- SIM
                                11- NAO""")
                                return False
                        except:
                                pass

        if msg_recebida == '1' or msg_recebida=='2' or msg_recebida== '3' or msg_recebida=='4':
                cursor.execute(f'SELECT departamento FROM tbdepartamentos WHERE id = 20')
                resposta = cursor.fetchall()
                resposta = resposta[0][0]
                texto = "Você será redirecionado para o departamento: "
                context.bot.send_message(chat_id=update.effective_chat.id,text=f"{texto} {resposta}")
                context.bot.send_message(chat_id=update.effective_chat.id,text=f"""Deseja encerrar o atendimento?
                10- SIM
                11- NAO""")
        elif msg_recebida == '10':
                cursor.execute(f"UPDATE `tbatendimento` SET `situacao` = 'F' WHERE `situacao` = 'A' AND `canal` = '3' AND `numero` = '{numero}'")
                context.bot.send_message(chat_id=update.effective_chat.id,text=f"Atendimento encerrado!")     
                dispatcher.remove_handler(opcoes_handler)
                dispatcher.remove_handler(tente_novamente_handler)
                banco.commit()

        else:
                context.bot.send_message(chat_id=update.effective_chat.id,text=f"Opção inválida selecione outra opção:\n{menu}")

# Fim verificação mensagem.




        # if update.message.text == '1':
        #         context.bot.send_message(chat_id=update.effective_chat.id, text='você escolheu a opção 1')
        # elif update.message.text == '2':
        #         context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('files/images.jpg', 'rb'))
        # elif update.message.text == '3':
        #         context.bot.send_video(chat_id=update.effective_chat.id,video=open('files/realshort.mp4', 'rb'), supports_streaming=True)
        # elif update.message.text == '4':
        #         context.bot.send_document(chat_id=update.effective_chat.id, document=open('files/report.pdf', 'rb'))
        # else:
        #         context.bot.send_message(chat_id=update.effective_chat.id,text=f"""Opção inválida, tente novamente:\n{menu}""")


# Caso usuário não envie contato entra nessa função
def tente_novamente(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text="""
        Por favor, envie seu contato para continuar. \nCaso estiver usando o telegram web clique no ícone demonstrado a seguir.
        """)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('files/icone_contato.png', 'rb'))
        

tente_novamente_handler = MessageHandler(Filters.text, tente_novamente)

opcoes_handler = MessageHandler(Filters.text, opcoes)


              

updater.start_polling()