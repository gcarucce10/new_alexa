import sys
import speech_recognition as sr

from audio.capture.mic_interface import MicInterface


class SpeechRecognizer(MicInterface):

    def __init__(self, device_index:int = None, verbose:bool = False,
                 timeout:int = 10, phrase_time_limit:int = 20,
                 pause_threshold:float = 0.8):
        super().__init__(device_index, verbose, timeout, phrase_time_limit, pause_threshold)
        self.recognizer = sr.Recognizer()


    def list_microphones(self):

        """Lista os microfones disponíveis."""
        """Configura o dispositivo de microfone"""

        print("Dispositivos de áudio disponíveis:", file=sys.stderr)
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"{index}: {name}", file=sys.stderr)


    def capture_speech(self):
        """Captura o áudio do microfone."""

        self.recognizer.pause_threshold = self.pause_threshold

        with sr.Microphone(device_index=2) as source:
            try:
                if self.verbose:
                    print(f"\nAguardando comando (Timeout: {self.timeout}s, Limite Frase: {self.phrase_time_limit}s, Pausa: {self.pause_threshold}s)...")
                else:
                    print(f"\nAguardando ativação (Pausa: {self.pause_threshold}s)...")

                # Ajusta ao ruído ANTES de cada escuta importante
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5) # Duração menor para ser mais rápido

                audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=self.phrase_time_limit)

                texto = self.recognizer.recognize_google(audio, language='pt-BR')
                if self.verbose:
                    print(f"\nVocê disse: {texto}")
                return texto
                
            except sr.WaitTimeoutError:
                if self.verbose: print("Tempo limite excedido.")
                return None
            except sr.UnknownValueError:
                if self.verbose: print("Não foi possível entender.")
                return None
            except Exception as e:
                if self.verbose: print(f"Erro no reconhecimento: {str(e)}")
                return None
       