from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# 1. Configuração da API do Gemini
genai.configure(api_key='AIzaSyCrTIkYIDZK6uBcFZe0KgxE9rn7xu8LNbI')  # Armazene sua chave em uma variável de ambiente

# 2. Inicialização do modelo
model = genai.GenerativeModel('gemini-2.0-flash')  # Você pode usar 'gemini-1.0-pro' para versão mais leve

@app.route('/processar_voz', methods=['POST'])
def processar_voz():
    dados = request.json
    texto_recebido = dados.get('texto', '').strip()
    
    if not texto_recebido:
        return jsonify({"resposta": "Nenhum texto recebido", "status": "error"}), 400
    
    print(f"Texto recebido: {texto_recebido}")

    try:
        # 3. Geração da resposta com Gemini
        response = model.generate_content(
            f"""Você é um assistente virtual inteligente. Responda de forma clara e concisa em português.
            Pergunta/Comando: {texto_recebido}
            Resposta:"""
        )
        
        resposta_gemini = response.text
        
        # 4. Log e retorno da resposta
        print(f"Resposta do Gemini: {resposta_gemini}")
        return jsonify({
            "resposta": resposta_gemini,
            "status": "success"
        })
        
    except Exception as e:
        print(f"Erro ao processar com Gemini: {str(e)}")
        return jsonify({
            "resposta": f"Erro no servidor: {str(e)}",
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)