import google.generativeai as genai
from AI_agent import IA_Agent
import json

# Define o caminho para o arquivo de pré-prompt
prompt_file = '/prompts/Current_Prompt.txt'  # Caminho para o arquivo de pré-prompt

class DefaultAnswer:
    text: str
    actions: list[str]

class GeminiAgent(IA_Agent):

    def __init__(self, api_key: str, model_name: str = 'gemini-2.0-flash', prompt_file_path: str = prompt_file) -> None:
        """
        Initializes the Gemini AI agent with the provided API key and system instructions.
        """
        genai.configure(api_key=api_key)
        
        self.api_key = api_key # Salva para possível reinicialização
        self.model_name = model_name # Salva para possível reinicialização
        self.prompt_file_path = prompt_file_path # Salva para possível reinicialização

        # Carrega o conteúdo do pré-prompt
        self.system_instruction_content = self._load_pre_prompt(self.prompt_file_path)

        # Configuração de geração, incluindo o schema JSON
        self.generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
            response_schema=DefaultAnswer 
        )

        # Inicializa o modelo com a system_instruction
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            system_instruction=self.system_instruction_content 
        )
        print(f"Modelo Gemini inicializado com instruções do sistema de '{self.prompt_file_path}'.")


    def respond(self, message: str) -> dict:
        """
        Generates a response to the given message using the pre-loaded system instructions.
        """
        try:
            # O pré-prompt já foi configurado como system_instruction,
            # então só precisamos enviar a mensagem do usuário.
            response = self.model.generate_content(contents=message)
            json_string = response.text
            try:
                json_response = json.loads(json_string)
                return json_response
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON da resposta da IA: {str(e)}")
                print(f"Resposta bruta da IA: {json_string.strip()}")
                return {
                    "error": "Formato JSON inválido da IA",
                    "details": str(e),
                    "raw_response": json_string.strip()
                }
        except Exception as e:
            print(f"Erro ao processar com Gemini: {str(e)}")
            # Adicionar mais detalhes do erro se possível, ex: response.prompt_feedback
            error_details = str(e)
            if hasattr(response, 'prompt_feedback'):
                 error_details += f" | Feedback do prompt: {response.prompt_feedback}"
            return {"error": "Erro no servidor Gemini", "details": error_details}


    def update_system_instructions(self, new_prompt_file_path: str | None = None):
        """
        Recarrega as instruções do sistema do arquivo e reinicializa o modelo.
        Se new_prompt_file_path não for fornecido, usa o caminho original.
        """
        if new_prompt_file_path:
            self.prompt_file_path = new_prompt_file_path
        
        print(f"Atualizando instruções do sistema de '{self.prompt_file_path}'...")
        self.system_instruction_content = self._load_pre_prompt(self.prompt_file_path)
        
        # Reinicializa o modelo com as novas instruções do sistema
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            system_instruction=self.system_instruction_content
        )
        print("Instruções do sistema atualizadas e modelo reinicializado.")
