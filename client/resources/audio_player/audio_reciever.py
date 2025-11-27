import socket
import pyaudio
import json
import struct
import threading
import queue
import time
import os
import numpy as np

# --- Configurações ---
buffer_audio = queue.Queue(maxsize=2000) 
pausado = False
playlist_concluida = False 

# Controle de Volume
volume_atual = 1.0      
volume_memoria = 1.0    

# Configuração do Socket de Comandos
HOST_COMANDOS = 'localhost'
PORTA_COMANDOS = 6000

# Variáveis globais de navegação
cliente_socket_atual = None  
indice_atual = 0             
comando_navegacao = None     
bloqueio_navegacao = threading.Lock() 

def ler_lista_reproducao():
    try:
        with open('lista_reproducao.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return sorted(dados.get("url-list", []), key=lambda x: x['track'])
    except:
        return []

# --- Thread de Comandos (Mantida igual, apenas resumida para foco) ---
def thread_escuta_comandos():
    global pausado, comando_navegacao, cliente_socket_atual, volume_atual, volume_memoria
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((HOST_COMANDOS, PORTA_COMANDOS))
        print(f"[COMANDO] Escutando ordens em {HOST_COMANDOS}:{PORTA_COMANDOS}...")
    except OSError:
        return

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            mensagem = json.loads(data.decode('utf-8'))
            acao = mensagem.get('acao')
            print(f"\n[COMANDO] >> {acao}")

            if acao == 'pausar_retomar':
                pausado = not pausado
            elif acao == 'volume_aumentar':
                volume_atual = min(2.0, volume_atual + 0.1)
                print(f"Vol: {int(volume_atual*100)}%")
            elif acao == 'volume_diminuir':
                volume_atual = max(0.0, volume_atual - 0.1)
                print(f"Vol: {int(volume_atual*100)}%")
            elif acao == 'volume_fundo':
                volume_memoria = volume_atual
                volume_atual = 0.2
            elif acao == 'volume_restaurar':
                volume_atual = volume_memoria
            elif acao == 'anterior':
                with bloqueio_navegacao: comando_navegacao = 'anterior'
                if cliente_socket_atual: 
                    try: cliente_socket_atual.close()
                    except: pass
            elif acao == 'proximo':
                with bloqueio_navegacao: comando_navegacao = 'proximo'
                if cliente_socket_atual: 
                    try: cliente_socket_atual.close()
                    except: pass
            elif acao == 'parar':
                os._exit(0) 
        except Exception as e:
            print(f"[ERRO CMD] {e}")

def thread_rede():
    global playlist_concluida, cliente_socket_atual, indice_atual, comando_navegacao
    
    lista_urls = ler_lista_reproducao()
    if not lista_urls: return

    while 0 <= indice_atual < len(lista_urls):
        item = lista_urls[indice_atual]
        host = item.get('host', 'localhost')
        port = item.get('port', 5000)
        track_id = item.get('track', 1)

        print(f"\n[REDE] --- Conectando Faixa {track_id} ---")
        
        while True:
            if comando_navegacao: break
            try:
                cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cliente_socket_atual = cliente 
                cliente.settimeout(5)
                cliente.connect((host, int(port)))
                
                # Envia Handshake (Offset 0, Track ID)
                cliente.sendall(struct.pack('QI', 0, int(track_id)))

                # --- LÓGICA DE CABEÇALHO ROBUSTA ---
                # 1. Ler tamanho do JSON (8 bytes)
                payload_size_struct = struct.calcsize('Q')
                buffer_recebido = b''
                while len(buffer_recebido) < payload_size_struct:
                    pkt = cliente.recv(4096)
                    if not pkt: break
                    buffer_recebido += pkt
                
                if len(buffer_recebido) < payload_size_struct:
                    cliente.close(); time.sleep(1); continue

                msg_size = struct.unpack('Q', buffer_recebido[:payload_size_struct])[0]
                
                # 2. Ler o JSON completo
                dados_acumulados = buffer_recebido[payload_size_struct:]
                while len(dados_acumulados) < msg_size:
                    pkt = cliente.recv(4096)
                    if not pkt: break
                    dados_acumulados += pkt
                
                # 3. Separar JSON do Áudio limpo
                # json_data = dados_acumulados[:msg_size] # (Se precisasse ler os metadados)
                sobra_audio = dados_acumulados[msg_size:]
                
                if sobra_audio: 
                    buffer_audio.put(sobra_audio)

                cliente.settimeout(None)
                
                # --- LOOP DE RECEBIMENTO DE ÁUDIO ---
                while True:
                    if comando_navegacao: break
                    try:
                        pkt = cliente.recv(4096)
                        if not pkt: break 
                        buffer_audio.put(pkt)
                    except OSError: break 

                cliente.close()
                
                if not comando_navegacao:
                    time.sleep(0.5)
                    with bloqueio_navegacao: indice_atual += 1
                break 

            except Exception as e:
                if comando_navegacao: break 
                print(f"[REDE] Erro/Aguardando... ({e})")
                time.sleep(2)
        
        # Lógica de troca de faixa
        with bloqueio_navegacao:
            if comando_navegacao == 'anterior':
                indice_atual = max(0, indice_atual - 1)
                with buffer_audio.mutex: buffer_audio.queue.clear()
            elif comando_navegacao == 'proximo':
                novo_indice = indice_atual + 1
                indice_atual = min(len(lista_urls) - 1, novo_indice)
                with buffer_audio.mutex: buffer_audio.queue.clear()
            comando_navegacao = None 
            lista_urls = ler_lista_reproducao()

    print("\n[REDE] Playlist Finalizada.")
    playlist_concluida = True

def iniciar_player():
    global pausado, playlist_concluida, volume_atual
    
    # Inicia as threads auxiliares
    threading.Thread(target=thread_rede, daemon=True).start()
    threading.Thread(target=thread_escuta_comandos, daemon=True).start()

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100, output=True)

    print("--- Player Iniciado ---")
    
    # Buffer de resíduo para garantir alinhamento de bytes
    residuo = b''

    try:
        while True:
            if not pausado:
                if not buffer_audio.empty():
                    # Pega novo chunk e junta com o que sobrou da última vez
                    data = residuo + buffer_audio.get()
                    
                    # --- CORREÇÃO DO CRASH E DO CHIADO ---
                    # Para int16 Stereo, precisamos de múltiplos de 4 bytes (2 bytes * 2 canais).
                    # No mínimo, precisamos de múltiplos de 2 bytes para o np.int16 não quebrar.
                    
                    resto = len(data) % 4 # Forçando alinhamento estéreo (mais seguro que 2)
                    
                    if resto != 0:
                        # Guarda os bytes que sobraram para o próximo ciclo
                        residuo = data[-resto:]
                        data = data[:-resto]
                    else:
                        residuo = b''

                    if len(data) == 0:
                        continue

                    # Processamento de Volume
                    if volume_atual != 1.0:
                        # Converte
                        audio_data = np.frombuffer(data, dtype=np.int16)
                        
                        # Multiplica (usando float temporariamente)
                        audio_data = audio_data * volume_atual
                        
                        # Clip para evitar estouro e conversão segura
                        audio_data = np.clip(audio_data, -32768, 32767)
                        
                        # Retorna para bytes
                        data = audio_data.astype(np.int16).tobytes()

                    stream.write(data)
                else:
                    if playlist_concluida: break
                    time.sleep(0.01) # Sleep menor para evitar latência
            else:
                time.sleep(0.1)

    except KeyboardInterrupt: pass
    finally:
        stream.stop_stream(); stream.close(); p.terminate()

if __name__ == "__main__":
    iniciar_player()