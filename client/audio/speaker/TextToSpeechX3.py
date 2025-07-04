import time
import pyttsx3
import threading
from audio.speaker.speaker_interface import SpeakerInterface
from audio.capture.azure_sr import SpeechRecognizer
import keyboard

class TextToSpeechX3(SpeakerInterface):

    def __init__(self, text_speed: float, volume: float):
        super().__init__(text_speed, volume)
        self.engine: pyttsx3.Engine = pyttsx3.init()
        self.engine.setProperty("rate", self.text_speed)
        self.engine.setProperty("volume", self.volume)

    def speak_text(self, text: str, stop_event: threading.Event = None):
        """Faz o sistema falar o texto fornecido, podendo ser interrompido."""
        if not text:
            return
        try:
            self.engine.say(text)
            self.engine.startLoop(False)  # Inicia o loop de eventos sem bloquear
            while self.engine.isBusy():
                if stop_event and stop_event.is_set():
                    self.engine.stop()
                    break
                self.engine.iterate()  # Processa eventos de fala
                time.sleep(0.1)       # Evita uso excessivo de CPU
            self.engine.endLoop()
        except RuntimeError as e:
            pass

    def wait_for_interruption_keyboard(self, keyboard_key: str = 'esc', stop_event: threading.Event = None):
        print("Esperando pela tecla de interrupção:", keyboard_key)
        keyboard.wait(keyboard_key)
        print(f"\nTecla {keyboard_key} pressionada. Interrompendo a fala...")
        if stop_event:
            stop_event.set()
        self.stop_engine()

    def wait_for_interruption_audio(self, speak_thread: threading.Thread, stop_event: threading.Event = None):
        sr = SpeechRecognizer(timeout=5, phrase_time_limit=5, pause_threshold=0.8)
        while speak_thread.is_alive():
            audio = sr.capture_speech()
            if audio and any(word in audio.lower() for word in ["parar", "interromper", "cancelar", "esc"]):
                print("\nComando de interrupção recebido. Interrompendo a fala...")
                if stop_event:
                    stop_event.set()
                self.stop_engine()
                return False
            if audio and any(word in audio.lower() for word in ["alexa", "alexia", "aleixo", "alexa", "alexander"]):
                print("\nComando de ativação recebido. Continuando a fala...")
                if stop_event:
                    stop_event.set()
                self.stop_engine()
                return True
        return False

    def stop_engine(self):
        """Interrompe a engine de fala."""
        self.engine.stop()
        

