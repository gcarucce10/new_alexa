
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os
import json


from AI.genaiAgent import genaiAgent as GeminiAgent
from Actions.actions_connector import Connector
from prompts.build_prompt import build_prompt

# Carrega variáveis de ambiente do arquivo .env
load_dotenv("server.env", override=True)  

# Define o caminho para o arquivo JSON de ações
actionsData_path = os.path.join("", "Actions")
actionsData_path = os.path.join(actionsData_path, "actions_data.json")
with open(actionsData_path, 'r', encoding='utf-8') as f:
            jsonData: dict = json.load(f)

# Define Flask app
app = Flask(__name__)

# Inicializa o agente de IA 
model = GeminiAgent(
    api_key=os.getenv("API_KEY"),
    model='gemini-2.0-flash-lite', 
    prompt_file_path=os.path.join("prompts", "Current_Prompt.txt")
)  

search_model = GeminiAgent(
    api_key=os.getenv("API_KEY"),
    model='gemini-2.0-flash',
    prompt_file_path=os.path.join("prompts", "normal_anwser.txt"),
    googleSearch=True,
)

@app.route('/update_config', methods=['POST'])
def update_config():
    # Atualiza o arquivo de configuração do servidor
    dados = request.json

    # Atualiza o arquivo JSON de configurações
    # IMPLEMENTAR

    # Reconstrói o prompt com as novas ações
    build_prompt()

    model.update_system_instructions()


# Rota para processar o prompt de voz
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
        response = model.generate_content(texto_recebido)
        
        resposta_gemini = response.get('text', 'Resposta não encontrada na resposta da IA')
        actions = response.get('actions', None)

        # Roda o que for necessário
        if actions:
            if actions[0] == "AI-Anwser":
                response = search_model.generate_content(texto_recebido)
                resposta_gemini = response.get('text', 'Resposta não encontrada na resposta da IA')
            else:
                conn = Connector(actions, jsonData, "server")
                if conn.run_program():
                    resposta_gemini = resposta_gemini + "\n" + conn.resultado.stdout
            

        # Envio da resposta e das ações 
        print(f"Resposta do Gemini: {resposta_gemini}")
        return jsonify({
            "anwser": resposta_gemini,
            "status": "success",
            "actions": actions
        })
        
    except Exception as e:
        print(f"Erro ao processar com Gemini: {str(e)}")
        return jsonify({
            "resposta": f"Erro no servidor: {str(e)}",
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)