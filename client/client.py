import os
import sys
import json
import time
import threading
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv


from actions.actions_connector import Connector
from audio.capture.azure_sr import SpeechRecognizer
from audio.speaker.TextToSpeechX3 import TextToSpeechX3

# Carrega variáveis de ambiente do arquivo .env
load_dotenv("client.env", override=True)  

# Define o caminho para o arquivo JSON de ações
actionsData_path = os.path.join("", "actions")
actionsData_path = os.path.join(actionsData_path, "actions_data.json")
with open(actionsData_path, 'r', encoding='utf-8') as f:
            jsonData: dict = json.load(f)


# Configurações
SERVER_URL = os.getenv("SERVER_URL")  # Substitua pelo IP do servidor



# Inicializa todas as acoes que estiverem marcadas para inicialização no startup
# Essas ações serão executadas em threads separadas para não bloquear o assistente
def initialize_actions():
    actions: list[dict] = jsonData.get("actions")

    threads = []
    startup_actions = [action for action in actions if action.get("init-in-startup")]

    # Para cada ação que deve ser inicializada, rode a em paralelo e crie um monitor na thread
    for action in startup_actions:
        connector = Connector([action["name"], "--init", "yes"], jsonData, "client", True)
        connector.run_program()

        thread = threading.Thread(target=connector.monitor_execution)
        threads.append(thread)
        thread.start()




def server_comunication(prompt: str):
    """Envia texto para o servidor e retorna a resposta"""
    try:
        payload = {"prompt": prompt}
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            SERVER_URL,
            json=payload,
            headers=headers,
            timeout=20  # Timeout de 20 segundos
        )
        
        response.raise_for_status()  # Levanta exceção para erros HTTP
        return response.json()
        
    except RequestException as e:
        print(f"Erro na comunicação com o servidor: {str(e)}", file=sys.stderr)
        return f"Desculpe, houve um erro ao conectar com o servidor: {str(e)}"
    except Exception as e:
        print(f"Erro inesperado: {str(e)}", file=sys.stderr)
        return "Desculpe, ocorreu um erro interno."



def main():
    """Loop principal do assistente"""
    print("Assistente virtual iniciado. Pressione Ctrl+C para sair.")

    # Inicializa a todas as ações que precisam ser inicializadas
    initialize_actions()
    
    print("Digite 1 para utilizar o sistema de voz e 2 para enviar via texto:")
    option = int(input(""))

    # Inicializa o reconhecimento de fala
    if option == 1:
        activation_recognizer = SpeechRecognizer(
                verbose=False, 
                timeout=7,           # Espera até 7s por algum som
                phrase_time_limit=4, # Máximo de 4s para falar "Alexa"
                pause_threshold=0.5  # Considera fim da fala após 0.5s de silêncio
            )
        speech_recognizer = SpeechRecognizer(
                verbose=True, 
                timeout=10,          # Espera até 10s
                phrase_time_limit=20,# Máximo de 20s para a pergunta
                pause_threshold=1.0  # Permite pausas de até 1s
            )
        
    if option == 1 or option == 2:
        speak = TextToSpeechX3(text_speed=240, volume=0.8)

    text_ready = False

    while option in [1,2]:
        try:
            # Opção de Voz
            if option == 1:
                print("Assistente ativado por voz. Fale 'Alexa' para iniciar.")
                text = activation_recognizer.capture_speech()

                if text and any(word in text.lower() for word in ["alexa", "alexia", "aleixa", "alixa", "alex", "alexander"]):
                    print("Assistente Ativada!")
                    speak.speak_text("Pois não?")  

                    text = speech_recognizer.capture_speech()
                    if text:
                        text_ready = True

            # Opção de Texto
            elif option == 2:
                text_ready = True
                print("Assistente ativado por texto. Digite sua pergunta a seguir:")
                text = input("")

            # Envia Texto ao servidor
            if text_ready:
                response_obj = server_comunication(text) 

                if isinstance(response_obj, str):
                    # Se for uma string, é um erro ou mensagem de falha
                    response = response_obj
                    actions = None
                else:
                    response = response_obj.get("anwser", None)
                    actions= response_obj.get("actions", [])

                for action in actions:
                    
                    # Parse Action
                    params = action.split(";")

                    if params[0] != "AI-Anwser" and params[0] != "music":

                        conn = Connector(params, jsonData, "client")
                        if conn.run_program():
                            if conn.wait == False:
                                response = response + "\n" + conn.resultado.stdout
                        

                # Inicia as threads de fala e interrupção
                print(f"Resposta do servidor: {response}")
                stop_event = threading.Event()
                speak_thread = threading.Thread(target=speak.speak_text, args=(response, stop_event))
                if option == 2:
                    stop_thread = threading.Thread(target=speak.wait_for_interruption_keyboard, args=('esc', stop_event))
                elif option == 1:
                    stop_thread = threading.Thread(target=speak.wait_for_interruption_audio, args=(speak_thread, stop_event))

                speak_thread.start()
                stop_thread.start()

                # Espera as threads terminarem
                speak_thread.join()
                stop_thread.join()

                text_ready = False


        except KeyboardInterrupt:
            print("\nEncerrando o assistente...")
            break
        except Exception as e:
            print(f"Erro crítico: {str(e)}", file=sys.stderr)
            time.sleep(5)
            


if __name__ == '__main__':
    main()
