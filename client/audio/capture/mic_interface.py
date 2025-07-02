from abc import ABC, abstractmethod

class MicInterface(ABC):

    @abstractmethod
    def __init__(self, device_index:int = None, verbose:bool = False, timeout:int = 10, phrase_time_limit:int = 20, pause_threshold:float = 0.8):
        """
        Inicializa a interface do microfone com os parâmetros fornecidos.
        
        :param device_index: Índice do dispositivo de microfone (padrão é None).
        :param verbose: Se True, ativa o modo verboso (padrão é False).
        :param timeout: Tempo máximo de espera para captura de áudio (padrão é 10 segundos).
        :param phrase_time_limit: Limite de tempo para a frase capturada (padrão é 20 segundos).
        :param pause_threshold: Tempo de pausa para considerar o fim da fala (padrão é 0.8 segundos).
        """
        self.device_index = device_index
        self.verbose = verbose
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        self.pause_threshold = pause_threshold

    @abstractmethod
    def list_microphones(self):
        """Lista os microfones disponíveis."""
        pass

    @abstractmethod
    def capture_speech(self):
        """Captura o áudio do microfone."""
        pass