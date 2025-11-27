import json
import os
import time
import requests
from datetime import datetime
import pyaudio
import wave

# --- Configurações ---
ARQUIVO_CONFIG = 'request.json'
ARQUIVO_SOM = 'alarme.wav'
ARQUIVO_DB = 'lembretes_salvos.json' 
_ACTIONS_REMINDER_ENDPOINT = "/get_reminders"

# --- Funções de Persistência (Salvar/Carregar) ---

def salvar_dados(lista_lembretes):
    """
    Salva a lista atual de lembretes no disco para não perder dados.
    """
    try:
        with open(ARQUIVO_DB, 'w') as f:
            json.dump(lista_lembretes, f, indent=4)
        print("[SISTEMA] Dados salvos em disco com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar dados: {e}")

def carregar_dados_salvos():
    """
    Carrega os lembretes salvos anteriormente, se existirem.
    """
    if not os.path.exists(ARQUIVO_DB):
        return []
    
    try:
        with open(ARQUIVO_DB, 'r') as f:
            dados = json.load(f)
        print(f"[SISTEMA] Recuperados {len(dados)} lembretes do arquivo salvo.")
        return dados
    except Exception as e:
        print(f"[ERRO] O arquivo salvo estava corrompido ou ilegível: {e}")
        return []

# --- Funções de Rede e Configuração ---

def carregar_e_apagar_config():
    """
    Verifica se o ficheiro config existe. Se sim, lê a URL e apaga o ficheiro.
    """
    if not os.path.exists(ARQUIVO_CONFIG):
        return None

    try:
        print("\n[INFO] Novo ficheiro de configuração detetado!")
        with open(ARQUIVO_CONFIG, 'r') as f:
            dados = json.load(f)
            url_servidor = dados.get('url')
        
        os.remove(ARQUIVO_CONFIG)
        print("[INFO] Configuração lida e ficheiro apagado.")
        return url_servidor
    except Exception as e:
        print(f"[ERRO] Falha ao ler configuração: {e}")
        return None

def obter_lembretes(url):
    """
    Acede ao servidor e retorna a lista de novos lembretes.
    """
    try:
        print(f"[REDE] A buscar dados em: {url}")
        resposta = requests.get(url)
        
        if resposta.status_code == 200:
            return resposta.json()
        else:
            print(f"[ERRO] Servidor retornou código {resposta.status_code}")
            return []
    except Exception as e:
        print(f"[ERRO] Conexão falhou: {e}")
        return []

# --- Funções de Lógica e Áudio ---

def tocar_som_pyaudio(arquivo):
    chunk = 1024
    try:
        wf = wave.open(arquivo, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(chunk)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(chunk)
        stream.stop_stream()
        stream.close()
        p.terminate()
    except Exception as e:
        print(f"[AUDIO] Erro ao tocar som: {e}")

def adicionar_sem_duplicar(lista_atual, novos_itens):
    """
    Adiciona novos lembretes à lista principal e retorna True se houve mudança.
    """
    alteracao_feita = False
    contador = 0
    
    for novo in novos_itens:
        existe = False
        for atual in lista_atual:
            # Comparamos mensagem e hora para identificar se é o mesmo
            if atual['message'] == novo['message'] and atual['time'] == novo['time']:
                existe = True
                break
        
        if not existe:
            lista_atual.append(novo)
            contador += 1
            alteracao_feita = True
    
    if contador > 0:
        print(f"[SISTEMA] {contador} novos lembretes adicionados.")
    
    return alteracao_feita

# --- Loop Principal ---

def iniciar_sistema():
    print("=== Sistema de Alertas (com Persistência) Iniciado ===")
    
    # 1. Carrega o que tínhamos salvo antes de fechar o programa
    todos_lembretes = carregar_dados_salvos()
    
    print(f"Monitorando... (Pressione Ctrl+C para sair)")

    while True:
        houve_mudanca = False # Flag para saber se precisamos salvar no disco

        # --- PASSO 1: Verificar se há nova configuração ---
        url = carregar_e_apagar_config()
        
        if url:
            url = url + _ACTIONS_REMINDER_ENDPOINT
            novos_dados = obter_lembretes(url)
            if novos_dados:
                # Se adicionou algo novo, marcamos que houve mudança
                if adicionar_sem_duplicar(todos_lembretes, novos_dados):
                    houve_mudanca = True

        # --- PASSO 2: Verificar horários e tocar alarme ---
        agora = datetime.now()
        agora_str = agora.strftime("%Y-%m-%d %H:%M")

        for item in todos_lembretes:
            if not item.get('processado'):
                if agora_str == item['time']:
                    print(f"\n[ALERTA TOCA] {item['message']} - {item['time']}")
                    
                    tocar_som_pyaudio(ARQUIVO_SOM)
                    
                    if item['frequency'] == 'once':
                        item['processado'] = True
                        print("[ALERTA] Lembrete marcado como concluído.")
                        # Como o status mudou para processado, houve mudança nos dados
                        houve_mudanca = True

        # --- PASSO 3: Persistência ---
        # Só escrevemos no disco se houver alterações para poupar recursos
        if houve_mudanca:
            salvar_dados(todos_lembretes)

        time.sleep(5)

if __name__ == "__main__":
    iniciar_sistema()