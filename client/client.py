import os
import sys
import json
import time
import threading
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv
from flask import Flask, request, jsonify


from resources.resource_controller import ResourceController
from audio.capture.azure_sr import SpeechRecognizer
from audio.speaker.TextToSpeechX3 import TextToSpeechX3


class Client():
    def __init__(self, voice_command = True):

        # Carrega variáveis de ambiente do arquivo .env
        load_dotenv("client.env", override=True) 

        self.resource_connector = ResourceController()
        self.resource_connector.init_all_resources()

        # Configurações
        self.SERVER_URL = os.getenv("SERVER_URL")  # Substitua pelo IP do servidor
        if not self.SERVER_URL:
            print("Erro: A variável de ambiente SERVER_URL não está definida.", file=sys.stderr)
            sys.exit(1)

        self.voice_command = voice_command
        
        if self.voice_command:
            self.activation_recognizer = SpeechRecognizer(
                    verbose=False, 
                    timeout=7,           # Espera até 7s por algum som
                    phrase_time_limit=4, # Máximo de 4s para falar "Alexa"
                    pause_threshold=0.5  # Considera fim da fala após 0.5s de silêncio
                )
            self.speech_recognizer = SpeechRecognizer(
                    verbose=True, 
                    timeout=10,          # Espera até 10s
                    phrase_time_limit=20,# Máximo de 20s para a pergunta
                    pause_threshold=1.0  # Permite pausas de até 1s
                )
        self.speak = TextToSpeechX3(text_speed=240, volume=0.8)



    def server_comunication(self, prompt: str):
        """Envia texto para o servidor e retorna a resposta"""
        try:
            payload = {"prompt": prompt}
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(
                self.SERVER_URL,
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
        


    def client_loop(self):
        while True:
            try:
                # Opção de Voz
                if self.voice_command:
                    print("Assistente ativado por voz. Fale 'Alexa' para iniciar.")
                    text = self.activation_recognizer.capture_speech()

                    if text and any(word in text.lower() for word in ["alexa", "alexia", "aleixa", "alixa", "alex", "alexander"]):
                        print("Assistente Ativada!")
                        self.speak.speak_text("Pois não?")  

                        text = self.speech_recognizer.capture_speech()
                        if text:
                            text_ready = True

                # Opção de Texto
                else:
                    text_ready = True
                    print("Assistente ativado por texto. Digite sua pergunta a seguir:")
                    text = input("")

                # Envia Texto ao servidor
                if text_ready:
                    response_obj = self.server_comunication(text) 

                    if isinstance(response_obj, str):
                        # Se for uma string, é um erro ou mensagem de falha
                        response = response_obj
                        resources = None
                    else:
                        response = response_obj.get("AI-Text", None)
                        resources = response_obj.get("resources", None)

                    if resources != []:
                        for r in resources:
                            self.resource_connector.send_request(r)
                      
                    if response != "":
                        # Inicia as threads de fala e interrupção
                        print(f"Resposta do servidor: {response}")
                        stop_event = threading.Event()
                        speak_thread = threading.Thread(target=self.speak.speak_text, args=(response, stop_event))
                        if not self.voice_command:
                            stop_thread = threading.Thread(target=self.speak.wait_for_interruption_keyboard, args=('esc', stop_event))
                        else:
                            stop_thread = threading.Thread(target=self.speak.wait_for_interruption_audio, args=(speak_thread, stop_event))

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



    def server_flask_app(self):
    
        app = Flask(__name__)

        @app.route('/get_config', methods=['GET'])
        def get_config():
            pass

        @app.route('/update_config', methods=['POST'])
        def update_config():
            pass

        @app.route('/send_message', methods=['POST'])
        def send_message():
            pass



                
if __name__ == '__main__':
    """Loop principal do assistente"""
    print("Assistente virtual iniciado. Pressione Ctrl+C para sair.")
    
    print("Digite 1 para utilizar o sistema de voz e 2 para enviar via texto:")
    option = int(input(""))

    clt = Client(voice_command = (option == 1))
    clt.client_loop()
