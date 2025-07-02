import sys
import pyttsx3
from audio.speaker.speaker_interface import SpeakerInterface

class TextToSpeechX3(SpeakerInterface):

    def __init__(self, text_speed: float, volume: float):
        super().__init__(text_speed, volume)
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", self.text_speed)
        self.engine.setProperty("volume", self.volume)

    def speak_text(self, text: str):
        """Faz o sistema falar o texto fornecido."""
        if not text:
            return
            
        try:
            print(f"Resposta: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Erro na síntese de voz: {str(e)}", file=sys.stderr)
