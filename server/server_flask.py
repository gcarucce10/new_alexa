import traceback
import sys
import threading

from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os
import json

from Actions.actions_server_connector import RemoteActionConnector
from AI.genaiAgent import genaiAgent as GeminiAgent
from prompts.build_prompt import build_prompt


class AIBridgeServer:

    def __init__(self):

        # Carrega variáveis de ambiente do arquivo .env
        load_dotenv("server.env", override=True)  

        # Inicializa o agente de IA 
        self.actions_model = GeminiAgent(
            api_key=os.getenv("API_KEY"),
            model='gemini-2.5-flash-lite', 
            prompt_file_path=os.path.join("prompts", "Actions_Prompt.txt")
        )  

        self.search_model = GeminiAgent(
            api_key=os.getenv("API_KEY"),
            model='gemini-2.5-flash',
            prompt_file_path=os.path.join("prompts", "search_prompt.txt"),
            googleSearch=True,
        )

        self.connector = RemoteActionConnector()


    
    def format_json_resource(params: list[str]):

        resource_name = params[0]


        json_data = {}
        values = []
        is_key = True # Key == True, Value == False

        for index in range(1, len(params)):

            param = params[index]

            # Is Key
            if is_key:
                if param == "--local":
                    break
                param = param.removeprefix("--")
                key = param
                is_key = False

            # Is Value
            else:

                # Value is a list
                if param.endswith(","):
                    param = param.removesuffix(",")
                    values.append(param)

                # Single value or last value in list
                else:
                    values.append(param)
                    if values.__len__() == 1:
                        # Single value, add directly
                        json_data[key] = values[0]
                    else:
                        # Multiple values, add as list
                        json_data[key] = values

                    # Reset for next key-value pair
                    values = []  
                    is_key = True 

        dictionary = {
                                            "resource": {
                                                "name": resource_name,
                                                "config": json_data
                                            }     
                                      }     

        return json_data
    

    


    def flask_server(self):

        # Define Flask app
        app = Flask(__name__)

        @app.route('/processar_voz', methods=['POST'])
        def process_prompt():

            dados = request.json

            if not dados or 'prompt' not in dados:
                return jsonify({"answer": "Dados inválidos", "status": "error"}), 400
            
            # 2. Extração do texto recebido
            texto_recebido = dados.get('prompt', '').strip()
            
            if not texto_recebido:
                return jsonify({"answer": "Nenhum texto recebido", "status": "error"}), 400
            
            
            print(f"Texto recebido: {texto_recebido}")

            try:

                # Geração da resposta com Gemini
                actions_response = self.actions_model.returnJson(texto_recebido)
                
                #resposta_gemini = response.get('text', 'Resposta não encontrada na resposta da IA')
                actions: list[str] = actions_response.get('actions', None)

                action_result: str = ""
                action_resources: list[dict] = []

                # Roda todas as acoes necessarias
                for action in actions: 
                        
                    # Conversa com IA com suporte a busca na internet
                    if action == "AI-Anwser":
                        search_model_response = self.search_model.generate_content(texto_recebido) 
                        self.actions_model.add_context(search_model_response)
                        search_model_response = search_model_response.replace("*", "")

                    else:
                        # Parse Action
                        params = action.split(";")

                        direct_resource = False

                        # Eh um comando pra ser rodado apenas local no resource?
                        for p in params:
                            if p == "--local":
                                direct_resource = True
                        
                        if direct_resource:
                            # audio_player --command next --local
                            action_resources.append(self.format_json_resource(params))  

                        else:
                            action_response: dict = self.connector.send_action_request(params)
                            print(action_response)  
                            action_text = str(action_response.get("result").get("result"))
                            action_resources.append(action_response.get("resources", ""))
                            action_result = action_result +"Essa foi a ação já executada " + action + ":\n" + action_text + "\n\n"
                        
                # Adiciona o resultado das ações ao contexto das IAs 
                # Somente se for necessario
                if "AI-Anwser" not in actions:   
                    action_result = "Essas foram as ações executadas e seus resultados, informe para o usuario qual foi o resultado atingido" + action_result

                    # Gera resposta completa com a IA com mais parametros
                    search_model_response = self.search_model.generate_content(action_result)

                # Envio da resposta e das ações 
                print(f"Resposta do Gemini: {search_model_response}")
                return jsonify({
                    "AI-Text": search_model_response,
                    "status": "success",
                    "resources": action_resources

                })
                
            except Exception as e:
                print(f"An error occurred: {e}")
                # Get the traceback information
                exc_type, exc_obj, exc_tb = sys.exc_info()
                # Extract the last frame of the traceback (where the error originated)
                tb_list = traceback.extract_tb(exc_tb)
                last_frame = tb_list[-1]

                filename = last_frame.filename
                line_number = last_frame.lineno
                function_name = last_frame.name
                code_line = last_frame.line

                print(f"Error details:")
                print(f"  File: {filename}")
                print(f"  Line: {line_number}")
                print(f"  Function: {function_name}")
                print(f"  Code: {code_line}")

                return jsonify({
                    "resposta": f"Erro no servidor: {str(e)}",
                    "status": "error"
                }), 500
            

        @app.route('/update_config', methods=['GET'])   
        def update_config():
            # Atualiza o arquivo de configuração do servidor
            path = os.path.join("", "prompts","Instruction.txt")

            self.connector.build_instruction_set(path)

            # Reconstrói o prompt com as novas ações
            build_prompt()

            self.actions_model.update_system_instructions()

            return jsonify ({
                "status": "ok"
            }), 200

        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False) 



# Rota para processar o prompt de voz

if __name__ == '__main__':
    server = AIBridgeServer()
    server.flask_server() 