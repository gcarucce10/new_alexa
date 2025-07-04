import json
import os

 # Garante que o caminho está correto
NOME_ARQUIVO_FILA = os.path.join(os.path.dirname(__file__), 'fila_de_reproducao.json')

def ler_fila():
    """Lê a fila de reprodução a partir do arquivo JSON.
    Se o arquivo não existir, retorna uma estrutura de fila vazia.
    """
    try:
        with open(NOME_ARQUIVO_FILA, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            # Garante que a chave 'fila' existe
            if 'fila' not in dados or not isinstance(dados['fila'], list):
                return {'fila': []}
            return dados
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existe ou está corrompido, começamos com uma fila vazia.
        return {'fila': []}

def escrever_fila(dados):
    """Escreve os dados fornecidos para o arquivo JSON da fila."""
    with open(NOME_ARQUIVO_FILA, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)