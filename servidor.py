from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/processar_voz', methods=['POST'])
def processar_voz():
    dados = request.json
    texto_recebido = dados.get('texto', '')
    print(f"Texto recebido: {texto_recebido}")
    
    # Processamento (exemplo: ecoar o texto)
    resposta = f"Servidor recebeu: '{texto_recebido}'. Obrigado!"
    
    return jsonify({"resposta": resposta})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)