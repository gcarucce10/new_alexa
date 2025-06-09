from abc import ABC, abstractmethod
import json

class Agent(ABC):
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
    def generate_content(self, message: str) -> str:
        """
        Generates a response to the given message.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def returnJson(self, message: str) -> dict:
        """
        Returns a JSON object from the given message.
        This method can be overridden by subclasses if needed.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def update_system_instructions(self, new_prompt_file_path: str | None = None):
        """
        Updates the system instructions from a file and reinitializes the model.
        If new_prompt_file_path is not provided, uses the original path.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    def _str_to_json(self, prompt: str) -> dict:
        """
        Converts a string to a JSON object.
        This method can be overridden by subclasses if needed.
        """
        try:
            json_response = json.loads(prompt)
            return json_response
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON da resposta da IA: {str(e)}")
            print(f"Resposta bruta da IA: {prompt}")
            return {
                "error": "Formato JSON inválido da IA",
                "details": str(e),
                "raw_response": prompt.strip()
            }
    
    # Carrega o pré-prompt de um arquivo
    def _load_pre_prompt(self, file_path: str | None) -> str:

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"Alerta: Arquivo de pré-prompt não encontrado em: {file_path}. Usando string vazia como instrução do sistema.")
            return "" 
        except Exception as e:
            print(f"Erro ao carregar o pré-prompt de {file_path}: {e}. Usando string vazia.")
            return ""
    