# Arquivo: tocador.py (ou o teu ...\actions\music\music.py do cliente)

import subprocess
import time
import os
import socket
import threading
import queue
import sys  # Importar o módulo sys
from datetime import datetime # Para adicionar data/hora aos logs

# As funções listen_for_control_messages e iniciar_ffplay continuam iguais.
def listen_for_control_messages(host, port, command_queue, stop_event):
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"[Controlo] A conectar ao servidor de controlo em {host}:{port}...")
            sock.connect((host, port))
            print("[Controlo] Conectado!")
            buffer = ""
            while not stop_event.is_set():
                data = sock.recv(1024).decode('utf-8')
                if not data:
                    raise ConnectionResetError
                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    print(f"[Controlo] Mensagem recebida: {message}")
                    command_queue.put(message)
        except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
            print(f"[Controlo] Conexão perdida ou recusada: {e}. A tentar novamente em 5s...")
            time.sleep(5)
        finally:
            if sock: sock.close()

def iniciar_ffplay(host='127.0.0.1', porta=1234):
    endereco = f'tcp://{host}:{porta}'
    comando = ['ffplay', '-nodisp', '-loglevel', 'error', '-autoexit', '-i', endereco]
    return subprocess.Popen(comando)

# A função main é a que vamos corrigir
def main():
    # --- BLOCO DE REDIRECIONAMENTO DE SAÍDA ---
    try:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(SCRIPT_DIR, 'tocador.log')
        
        # 'a' para adicionar ao final do arquivo
        log_file = open(log_file_path, 'a', encoding='utf-8')
        
        # Redireciona stdout e stderr para o nosso arquivo de log
        sys.stdout = log_file
        sys.stderr = log_file
        
        print(f"\n--- Log do Tocador iniciado em: {datetime.now()} ---")
    except Exception as e:
        # Se falhar, imprime na consola original
        print(f"ERRO CRÍTICO ao configurar o log: {e}")

    # --- O resto do programa ---
    SERVER_HOST = '127.0.0.1'
    command_queue = queue.Queue()
    stop_event = threading.Event()

    control_thread = threading.Thread(
        target=listen_for_control_messages,
        args=(SERVER_HOST, 1235, command_queue, stop_event),
        daemon=True
    )
    control_thread.start()

    processo_ffplay = None
    musica_alvo_path = None
    musica_em_reproducao_path = None

    print("--- Tocador (v3.4 - Saída Independente) ---")
    try:
        while not stop_event.is_set():
            try:
                mensagem = command_queue.get_nowait()
                if mensagem.startswith("PLAY:"):
                    musica_alvo_path = mensagem.split(":", 1)[1]
                elif mensagem == "STOP":
                    musica_alvo_path = None
            except queue.Empty:
                pass 

            if musica_alvo_path != musica_em_reproducao_path:
                if processo_ffplay:
                    processo_ffplay.kill()
                    processo_ffplay.wait()
                    processo_ffplay = None
                
                musica_em_reproducao_path = None

                if musica_alvo_path:
                    print(f"▶ A tentar iniciar ffplay para: {os.path.basename(musica_alvo_path)}")
                    try:
                        processo_ffplay = iniciar_ffplay()
                        musica_em_reproducao_path = musica_alvo_path
                    except FileNotFoundError:
                        print("\n!!! ERRO CRÍTICO: 'ffplay' não foi encontrado. !!!")
                        break 
                    except Exception as e_popen:
                        print(f"\n!!! ERRO CRÍTICO ao iniciar ffplay: {e_popen}!!!")
                        break
            
            if processo_ffplay and processo_ffplay.poll() is not None:
                print(f"✔ ffplay terminou (música '{os.path.basename(musica_em_reproducao_path)}' acabou).")
                processo_ffplay = None
                musica_em_reproducao_path = None
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nPedido de encerramento pelo utilizador...")
    except Exception as e_main:
        print(f"\nERRO INESPERADO NO LOOP PRINCIPAL DO TOCADOR: {e_main}")
    finally:
        stop_event.set() 
        if processo_ffplay:
            processo_ffplay.kill()
        print("Tocador finalizado.")


if __name__ == '__main__':
    main()