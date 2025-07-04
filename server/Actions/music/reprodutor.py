# Arquivo: reprodutor.py

import subprocess
import time
import os
import gerenciador_fila
import socket
import threading
import sys  # Importar o módulo sys
from datetime import datetime # Para adicionar data/hora aos logs

# As funções auxiliares e a classe ControlServer continuam iguais.
# ... (copiar aqui as funções parar_stream_ffmpeg, iniciar_stream_ffmpeg e a classe ControlServer da versão anterior) ...
def parar_stream_ffmpeg(processo):
    if not processo: return
    # Adicionamos "print" para o log funcionar
    print("[Áudio] A parar stream de áudio atual...")
    try:
        processo.terminate()
        processo.wait(timeout=2.0)
    except subprocess.TimeoutExpired:
        processo.kill()
        processo.wait()

def iniciar_stream_ffmpeg(caminho_musica, host='127.0.0.1', porta=1234):
    comando = ['ffmpeg', '-re', '-i', caminho_musica, '-map', '0:a', '-c:a', 'aac', '-b:a', '192k', '-f', 'mpegts', f'tcp://{host}:{porta}?listen=1']
    return subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

class ControlServer:
    def __init__(self, host='0.0.0.0', port=1235):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.clients = []
        self.lock = threading.Lock()

    def _listen_for_clients(self):
        self.server_socket.listen(5)
        print(f"[Controlo] Servidor de controlo a escutar na porta {self.server_socket.getsockname()[1]}")
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"[Controlo] Novo cliente de controlo conectado: {addr}")
                with self.lock:
                    self.clients.append(client_socket)
            except OSError:
                break

    def broadcast(self, message):
        print(f"[Controlo] A transmitir mensagem: {message}")
        with self.lock:
            for client in self.clients[:]:
                try:
                    client.sendall((message + '\n').encode('utf-8'))
                except (ConnectionResetError, BrokenPipeError):
                    print(f"[Controlo] Cliente desconectado. A remover.")
                    self.clients.remove(client)
                    client.close()
    
    def start(self):
        thread = threading.Thread(target=self._listen_for_clients, daemon=True)
        thread.start()
    
    def shutdown(self):
        print("[Controlo] A desligar servidor de controlo...")
        with self.lock:
            for client in self.clients:
                client.close()
        self.server_socket.close()


def main_reprodutor():
    # --- BLOCO DE REDIRECIONAMENTO DE SAÍDA ---
    # Obter o diretório onde o script está para guardar o log lá
    try:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(SCRIPT_DIR, 'reprodutor.log')
        
        # 'a' significa 'append' (adicionar ao final), para não perder logs antigos
        log_file = open(log_file_path, 'a', encoding='utf-8')
        
        # Redireciona a saída padrão e de erros para o nosso arquivo de log
        sys.stdout = log_file
        sys.stderr = log_file
        
        print(f"\n--- Log iniciado em: {datetime.now()} ---")

    except Exception as e:
        # Se o redirecionamento falhar, imprime o erro na consola original
        print(f"ERRO CRÍTICO ao configurar o log: {e}")

    # O resto do programa continua normalmente, mas agora todos os 'print()'
    # irão para o arquivo 'reprodutor.log'.
    
    control_server = ControlServer()
    control_server.start()
    
    processo_ffmpeg = None
    musica_atual_tocando = None
    
    print("--- Reprodutor (v2.5 - Saída Independente) ---")
    try:
        while True:
            if processo_ffmpeg and processo_ffmpeg.poll() is not None:
                print(f"✔ [Áudio] Stream da música '{os.path.basename(musica_atual_tocando)}' terminou naturalmente.")
                dados_atuais = gerenciador_fila.ler_fila()
                if dados_atuais.get('fila') and dados_atuais['fila'][0] == musica_atual_tocando:
                    dados_atuais['fila'].pop(0)
                    gerenciador_fila.escrever_fila(dados_atuais)
                    print("↪ Fila atualizada, avançando para a próxima.")
                processo_ffmpeg = None
                musica_atual_tocando = None
            
            dados_fila = gerenciador_fila.ler_fila()
            fila = dados_fila.get('fila', [])
            proxima_na_fila = fila[0] if fila else None

            if proxima_na_fila != musica_atual_tocando:
                parar_stream_ffmpeg(processo_ffmpeg)
                processo_ffmpeg = None
                
                if proxima_na_fila:
                    print(f"▶ [Áudio] A iniciar stream para: {os.path.basename(proxima_na_fila)}")
                    processo_ffmpeg = iniciar_stream_ffmpeg(proxima_na_fila)
                    control_server.broadcast(f"PLAY:{proxima_na_fila}")
                else:
                    if musica_atual_tocando is not None:
                        print("⏹ [Áudio] Fila vazia. Parando a reprodução.")
                        control_server.broadcast("STOP")
                
                musica_atual_tocando = proxima_na_fila
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPedido de encerramento recebido (KeyboardInterrupt)...")
    except Exception as e:
        print(f"\nERRO INESPERADO NO LOOP PRINCIPAL: {e}") # Captura qualquer outro erro
    finally:
        parar_stream_ffmpeg(processo_ffmpeg)
        control_server.shutdown()
        print("Reprodutor encerrado.")
