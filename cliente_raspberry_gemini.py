import speech_recognition as sr
import pyttsx3
import requests
import time
import sys
from requests.exceptions import RequestException

# Configurações
SERVER_URL = "http://192.168.1.3:5000/processar_voz"  # Substitua pelo IP do servidor
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Configurações de voz
engine.setProperty('rate', 180)  # Velocidade da fala
engine.setProperty('volume', 0.9)  # Volume (0.0 a 1.0)

def configurar_microfone():
    """Configura o dispositivo de microfone"""
    print("Dispositivos de áudio disponíveis:", file=sys.stderr)
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{index}: {name}", file=sys.stderr)
    
    # Use o índice correto do seu microfone
    return sr.Microphone(device_index=2)

def capturar_voz(verbose=False):
    """Captura áudio do microfone e converte para texto"""
    with configurar_microfone() as source:
        try:
            if verbose:
                print("\nAguardando comando de voz...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
            
            texto = recognizer.recognize_google(audio, language='pt-BR')
            if verbose:
                print(f"\nVocê disse: {texto}")
            return texto
            
        except sr.WaitTimeoutError:
            if verbose:
                print("Tempo limite excedido. Nenhum áudio detectado.")
            return None
        except sr.UnknownValueError:
            if verbose:
                print("Não foi possível entender o áudio.")
            return None
        except Exception as e:
            if verbose:
                print(f"Erro inesperado no reconhecimento: {str(e)}")
            return None

def enviar_para_servidor(texto):
    """Envia texto para o servidor e retorna a resposta"""
    try:
        payload = {"texto": texto}
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            SERVER_URL,
            json=payload,
            headers=headers,
            timeout=10  # Timeout de 10 segundos
        )
        
        response.raise_for_status()  # Levanta exceção para erros HTTP
        return response.json().get('resposta')
        
    except RequestException as e:
        print(f"Erro na comunicação com o servidor: {str(e)}", file=sys.stderr)
        return f"Desculpe, houve um erro ao conectar com o servidor: {str(e)}"
    except Exception as e:
        print(f"Erro inesperado: {str(e)}", file=sys.stderr)
        return "Desculpe, ocorreu um erro interno."

def falar(texto):
    """Sintetiza a resposta em voz"""
    if not texto:
        return
        
    try:
        print(f"Resposta: {texto}")
        engine.say(texto)
        engine.runAndWait()
    except Exception as e:
        print(f"Erro na síntese de voz: {str(e)}", file=sys.stderr)

def main():
    """Loop principal do assistente"""
    print("Assistente virtual iniciado. Pressione Ctrl+C para sair.")
    
    while True:
        try:
            print("Esperando Ativação")
            texto = capturar_voz()
            if texto and (texto.lower() in ["alexa", "alexia", "aleixa", "alixa"]):
                print("Assistente Ativada!")
                texto = capturar_voz(True)
                if texto:
                    resposta = enviar_para_servidor(texto)
                    falar(resposta)
                
            time.sleep(2)  # Pequena pausa entre interações
            
        except KeyboardInterrupt:
            print("\nEncerrando o assistente...")
            break
        except Exception as e:
            print(f"Erro crítico: {str(e)}", file=sys.stderr)
            time.sleep(5)  # Espera antes de tentar novamente

if __name__ == '__main__':
    main()