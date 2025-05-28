import google.generativeai as genai
import AI_agent
import json

# Define o caminho para o arquivo de pré-prompt
prompt_file = '/AI/prompts/VirtualAssistant.txt'  # Caminho para o arquivo de pré-prompt

class GeminiAgent(AI_agent):

    def __init__(self, api_key: str, model: str = 'gemini-2.5-flash') -> None:
        
        """
        Initializes the Gemini AI agent with the provided API key.
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.pre_prompt = self._load_pre_prompt(prompt_file) # Carrega o pré-prompt na inicialização

    # Carrega o pré-prompt de um arquivo
    def _load_pre_prompt(self, file_path: str) -> str:
        """
        Loads the pre-prompt text from the specified file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"Erro: O arquivo de pré-prompt '{file_path}' não foi encontrado.")
            return "Você é um assistente virtual inteligente. Responda de forma clara e concisa em português.\nPergunta/Comando:" # Fallback
        except Exception as e:
            print(f"Erro ao carregar o arquivo de pré-prompt: {str(e)}")
            return "Você é um assistente virtual inteligente. Responda de forma clara e concisa em português.\nPergunta/Comando:" # Fallback

    # Retorna um dicionário com o JSON esperado
    def respond(self, message: str) -> dict: 
        """
        Generates a response to the given message using the loaded pre-prompt,
        expecting a JSON output.
        """
        try:
            full_prompt = f"{self.pre_prompt} {message}"
            response = self.model.generate_content(full_prompt)
            
            # Tenta analisar a resposta como JSON
            try:
                json_response = json.loads(response.text.strip())
                return json_response
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON da resposta da IA: {str(e)}")
                print(f"Resposta bruta da IA: {response.text.strip()}")
                return {"erro": "Formato JSON inválido da IA", "detalhes": str(e), "resposta_bruta": response.text.strip()}
        except Exception as e:
            print(f"Erro ao processar com Gemini: {str(e)}")
            return {"erro": "Erro no servidor", "detalhes": str(e)}