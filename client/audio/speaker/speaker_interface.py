from abc import ABC, abstractmethod

class SpeakerInterface(ABC):

    @abstractmethod
    def __init__(self, text_speed: float, volume: float):
        """
        Inicializa a interface do microfone com os parâmetros fornecidos.
        
        :param device_index: Índice do dispositivo de microfone (padrão é None).
        :param verbose: Se True, ativa o modo verboso (padrão é False).
        :param timeout: Tempo máximo de espera para captura de áudio (padrão é 10 segundos).
        :param phrase_time_limit: Limite de tempo para a frase capturada (padrão é 20 segundos).
        :param pause_threshold: Tempo de pausa para considerar o fim da fala (padrão é 0.8 segundos).
        """
        self.text_speed = text_speed
        self.volume = volume
        
    @abstractmethod
    def speak_text(self, text: str):
        """Faz o sistema falar o texto fornecido."""
        pass

    