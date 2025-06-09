# To run this code you need to install the following dependencies:
# pip install google-genai

from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

from AI.Agent import Agent 

class genaiAgent(Agent):
    """
    An abstract base class for AI agents.
    """
    def __init__(self, api_key: str, prompt_file_path: str, model: str="gemini-2.0-flash-lite", googleSearch: bool = False) -> None:
        """
        Initializes the AI agent with a name.
        """

        self.model = model

        self.client = genai.Client(
        api_key=api_key,
        )

        if googleSearch:
            self.tools = [
                types.Tool(google_search=types.GoogleSearch()),
            ]
        else:
            self.tools = []

        self.generate_content_config = types.GenerateContentConfig(
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_ONLY_HIGH",  # Block few
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_ONLY_HIGH",  # Block few
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_ONLY_HIGH",  # Block few
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",  # Block few
                ),
            ],
            response_mime_type="application/json",
            response_schema=types.Schema(
                type = types.Type.OBJECT,
                required = ["text"],
                properties = {
                    "text": types.Schema(
                        type = types.Type.STRING,
                    ),
                    "actions": types.Schema(
                        type = types.Type.ARRAY,
                        items = types.Schema(
                            type = types.Type.STRING,
                        ),
                    ),
                },
            ),
            system_instruction=[
                types.Part.from_text(text=self._load_pre_prompt(prompt_file_path)),
            ],
            tools=self.tools,
        )

        self.chat = self.client.chats.create(
            model=model,
            config=self.generate_content_config,
        )


    def generate_content(self, message: str) -> str:
        """
        Generates a response to the given message.
        This method should be implemented by subclasses.
        """
        try:
            response = self.chat.send_message(message)
            print(f"Resposta bruta da IA: {response.text}")

            # Processa a resposta e retorna o texto
            return response.text
        except Exception as e:
            print(f"Erro ao processar com Gemini: {str(e)}")
            # Adicionar mais detalhes do erro se possível, ex: response.prompt_feedback
            error_details = str(e)
            return {"error": "Erro no servidor Gemini", "details": error_details}
    

    def returnJson(self, message: str) -> dict:
        """
        Returns a JSON object from the given message.
        This method can be overridden by subclasses if needed.
        """
        
        json_response = self._str_to_json(self.generate_content(message))
        return json_response
        

    def update_system_instructions(self, new_prompt_file_path: str | None = None):
        """
        Updates the system instructions from a file and reinitializes the model.
        If new_prompt_file_path is not provided, uses the original path.
        This method should be implemented by subclasses.
        """

        # Se new_prompt_file_path for fornecido, atualiza o caminho do arquivo de prompt
        if new_prompt_file_path:
            self.generate_content_config = types.GenerateContentConfig(
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="BLOCK_ONLY_HIGH",  # Block few
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="BLOCK_ONLY_HIGH",  # Block few
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_ONLY_HIGH",  # Block few
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_ONLY_HIGH",  # Block few
                    ),
                ],
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type = types.Type.OBJECT,
                    required = ["text"],
                    properties = {
                        "text": types.Schema(
                            type = types.Type.STRING,
                        ),
                        "actions": types.Schema(
                            type = types.Type.ARRAY,
                            items = types.Schema(
                                type = types.Type.STRING,
                            ),
                        ),
                    },
                ),
                system_instruction=[
                    types.Part.from_text(text=self._load_pre_prompt(new_prompt_file_path)),
                ],
                tools=self.tools,
            )

        # Reinicializa o modelo e chat com as novas instruções do sistema
        self.chat = self.client.chats.create(
            model=model,
            config=self.generate_content_config,
        )


if __name__ == "__main__":
    load_dotenv("server.env", override=True)  


    model = genaiAgent(
        api_key=os.getenv("API_KEY"),
        prompt_file_path=os.path.join("..", "prompts","Current_Prompt.txt"),
        model="gemini-2.0-flash-lite"
    )

    while True:
        user_input = input("Digite sua mensagem para a IA: ")
        if user_input.lower() in ['sair', 'exit', 'quit']:
            print("Saindo do loop.")
            break
        
        # Chama a função de geração com o texto do usuário
        response = model.returnJson(user_input)
        print(f"Resposta da IA: {response.get('text', 'Nenhuma resposta recebida')}")
