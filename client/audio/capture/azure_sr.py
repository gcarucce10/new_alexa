import os
import azure.cognitiveservices.speech as speechsdk
import sys

from dotenv import load_dotenv
from audio.capture.mic_interface import MicInterface

load_dotenv("client.env", override=True)  # Carrega variáveis de ambiente do arquivo .env

AZURE_KEY = os.getenv("AZURE_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")

class SpeechRecognizer(MicInterface):
    def __init__(self, device_index: int = None, verbose: bool = False, timeout: int = 10, phrase_time_limit: int = 20, pause_threshold: float = 0.8):
        super().__init__(device_index, verbose, timeout, phrase_time_limit, pause_threshold)
        
        # Configurar Azure Speech
        self.speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
        self.speech_config.speech_recognition_language = "pt-BR"
        
        # Configurar áudio
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
        # Criar reconhecedor
        self.recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, 
            audio_config=self.audio_config
        )
    
    def list_microphones(self):
        print("Usando microfone padrão do sistema", file=sys.stderr)
        print("Azure Speech Services configurado para pt-BR", file=sys.stderr)
    
    def capture_speech(self):
        try:
            if self.verbose:
                print(f"\nAguardando comando (Timeout: {self.timeout}s)...")
            else:
                print(f"\nAguardando ativação...")
            
            # Reconhecimento único
            result = self.recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                if self.verbose:
                    print(f"\nVocê disse: {result.text}")
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                if self.verbose: 
                    print("Não foi possível entender.")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                if self.verbose: 
                    print("Reconhecimento cancelado.")
                return None
            else:
                if self.verbose: 
                    print("Erro no reconhecimento.")
                return None
                
        except Exception as e:
            if self.verbose: 
                print(f"Erro no reconhecimento: {str(e)}")
            return None