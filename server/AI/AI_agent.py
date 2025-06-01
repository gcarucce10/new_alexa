from abc import ABC, abstractmethod


class IA_Agent(ABC):
    """
    An abstract base class for AI agents.
    """
    @abstractmethod
    def __init__(self, api_key: str, model: str) -> None:
        """
        Initializes the AI agent with a name.
        """
        raise NotImplementedError("Subclasses must implement this method.")


    @abstractmethod
    def respond(self, message: str) -> dict:
        """
        Generates a response to the given message.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    # Carrega o pré-prompt de um arquivo
    def _load_pre_prompt(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"Alerta: Arquivo de pré-prompt não encontrado em: {file_path}. Usando string vazia como instrução do sistema.")
            return "" 
        except Exception as e:
            print(f"Erro ao carregar o pré-prompt de {file_path}: {e}. Usando string vazia.")
            return ""
    