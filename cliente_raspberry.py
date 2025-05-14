import speech_recognition as sr
import pyttsx3
import requests
import json

# Configurações
SERVER_URL = "http://192.168.1.7:5000/processar_voz"  # Substitua pelo IP do computador
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def capturar_voz():
    with sr.Microphone(device_index=2) as source:  # Adicione esta linha
        recognizer.adjust_for_ambient_noise(source)  # Reduz ruído
        print("Diga algo...")
        audio = recognizer.listen(source, timeout=5)  # Timeout de 5 segundos
        
        try:
            #print("AAAAAAAAAAA\n\n\n\n\n\n\n\nAAAAAAAAAAAAAA")
            texto = recognizer.recognize_google(audio, language='pt-BR')
            print("Você disse:", texto)
            return texto
        except Exception as e:
            print("Erro no reconhecimento:", e)
            return None

def enviar_para_servidor(texto):
    try:
        payload = {"texto": texto}
        response = requests.post(SERVER_URL, json=payload)
        return response.json()['resposta']
    except Exception as e:
        print("Erro na comunicação com o servidor:", e)
        return None

def falar(texto):
    engine.say(texto)
    engine.runAndWait()

if __name__ == '__main__':
    while True:
        texto = capturar_voz()
        if texto:
            resposta = enviar_para_servidor(texto)
            if resposta:
                print("Resposta do servidor:", resposta)
                falar(resposta)