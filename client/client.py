from dotenv import load_dotenv
import os
import json
import speech_recognition as sr
import pyttsx3
import requests
import time
import sys
from requests.exceptions import RequestException

from actions.actions_connector import Connector

# Carrega variáveis de ambiente do arquivo .env
load_dotenv("client.env", override=True)  

# Define o caminho para o arquivo JSON de ações
actionsData_path = os.path.join("", "Actions")
actionsData_path = os.path.join(actionsData_path, "actions_data.json")
with open(actionsData_path, 'r', encoding='utf-8') as f:
            jsonData: dict = json.load(f)


# Configurações
SERVER_URL = os.getenv("SERVER_URL")  # Substitua pelo IP do servidor
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Configurações de voz
engine.setProperty('rate', 180)  # Velocidade da fala
engine.setProperty('volume', 0.9)  # Volume (0.0 a 1.0)

def list_microphones():
    """Configura o dispositivo de microfone"""
    print("Dispositivos de áudio disponíveis:", file=sys.stderr)
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{index}: {name}", file=sys.stderr)
    

def capture_speech(verbose=False, timeout=10, phrase_time_limit=20, pause_threshold=0.8):
    """Captura áudio do microfone com parâmetros ajustáveis."""
    
    # Define o pause_threshold específico para esta chamada
    recognizer.pause_threshold = pause_threshold
    
    with sr.Microphone(device_index=2) as source:
        try:
            if verbose:
                print(f"\nAguardando comando (Timeout: {timeout}s, Limite Frase: {phrase_time_limit}s, Pausa: {pause_threshold}s)...")
            else:
                 print(f"\nAguardando ativação (Pausa: {pause_threshold}s)...")

            # Ajusta ao ruído ANTES de cada escuta importante
            recognizer.adjust_for_ambient_noise(source, duration=0.5) # Duração menor para ser mais rápido
            
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            texto = recognizer.recognize_google(audio, language='pt-BR')
            if verbose:
                print(f"\nVocê disse: {texto}")
            return texto
            
        except sr.WaitTimeoutError:
            if verbose: print("Tempo limite excedido.")
            return None
        except sr.UnknownValueError:
            if verbose: print("Não foi possível entender.")
            return None
        except Exception as e:
            if verbose: print(f"Erro no reconhecimento: {str(e)}")
            return None



def server_comunication(prompt: str):
    """Envia texto para o servidor e retorna a resposta"""
    try:
        payload = {"prompt": prompt}
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            SERVER_URL,
            json=payload,
            headers=headers,
            timeout=10  # Timeout de 10 segundos
        )
        
        response.raise_for_status()  # Levanta exceção para erros HTTP
        return response.json()
        
    except RequestException as e:
        print(f"Erro na comunicação com o servidor: {str(e)}", file=sys.stderr)
        return f"Desculpe, houve um erro ao conectar com o servidor: {str(e)}"
    except Exception as e:
        print(f"Erro inesperado: {str(e)}", file=sys.stderr)
        return "Desculpe, ocorreu um erro interno."


def speak(text: str):
    """Sintetiza a resposta em voz"""
    if not text:
        return
        
    try:
        print(f"Resposta: {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Erro na síntese de voz: {str(e)}", file=sys.stderr)

def main():
    """Loop principal do assistente"""
    print("Assistente virtual iniciado. Pressione Ctrl+C para sair.")
    
    while True:
        try:
            # --- CHAMADA PARA ATIVAÇÃO (Mais sensível e rápida) ---
            texto_ativacao = capture_speech(
                verbose=False, 
                timeout=7,           # Espera até 7s por algum som
                phrase_time_limit=4, # Máximo de 4s para falar "Alexa"
                pause_threshold=0.5  # Considera fim da fala após 0.5s de silêncio
            )

            if texto_ativacao and any(palavra in texto_ativacao.lower() for palavra in ["alexa", "alexia", "aleixa", "alixa"]):
                print("Assistente Ativada!")
                speak("Pois não?") # Opcional: Dar um feedback sonoro

                # --- CHAMADA PARA PERGUNTA (Mais tolerante) ---
                texto_pergunta = capture_speech(
                    verbose=True, 
                    timeout=10,          # Espera até 10s
                    phrase_time_limit=20,# Máximo de 20s para a pergunta
                    pause_threshold=1.0  # Permite pausas de até 1s
                )

                if texto_pergunta:
                    # --- Separação das funções de enviar e receber ---
                    response_obj = server_comunication(texto_pergunta) 
                    resposta = response_obj.get("anwser", "Desculpe, não entendi a resposta do servidor.")
                    actions= response_obj.get("actions", [])

                    if actions:
                        conn = Connector(actions, jsonData, "server")
                        if conn.run_program():
                            resposta = resposta + "\n" + conn.resultado.stdout


                    speak(resposta) # Assumindo que 'resposta' já é o texto limpo
            
            # Não precisa de time.sleep(2) aqui, pois o timeout já causa uma pausa.
            # Se quiser uma pausa *garantida*, mantenha ou ajuste.
            # time.sleep(1) 

        except KeyboardInterrupt:
            print("\nEncerrando o assistente...")
            break
        except Exception as e:
            print(f"Erro crítico: {str(e)}", file=sys.stderr)
            time.sleep(5)  # Espera antes de tentar novamente

if __name__ == '__main__':
    main()