import json
import os

NOME_ARQUIVO_FILA = os.path.join(os.path.dirname(__file__), 'fila_de_reproducao.json')

def ler_fila():
    try:
        with open(NOME_ARQUIVO_FILA, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'fila': []}

def obter_arquivo_por_track_id(track_id):
    """
    Retorna o nome do arquivo baseado no track_id (1, 2, 3...).
    Assume que track 1 = índice 0 da lista.
    """
    dados = ler_fila()
    fila = dados.get('fila', [])
    
    # Converte Track ID (1-based) para Índice (0-based)
    indice = track_id - 1
    
    if 0 <= indice < len(fila):
        return fila[indice]
    
    return None