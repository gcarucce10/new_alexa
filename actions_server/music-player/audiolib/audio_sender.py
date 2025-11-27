import socket
import wave
import json
import struct
import time
import os
import gerenciador_fila as fila_manager

def iniciar_servidor():
    HOST = 'localhost'
    PORT = 5000
    CHUNK = 2048

    print(f"--- Servidor de Áudio (Sob Demanda) ---")

    while True:
        print(f"\nAguardando conexão em {PORT}...")
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen(1)

        conn, addr = servidor.accept()
        print(f"Conectado a: {addr}")

        try:
            # --- NOVO HANDSHAKE ---
            # Recebe 12 bytes: 8 bytes (Offset) + 4 bytes (Track ID)
            header_data = conn.recv(12)
            if not header_data:
                conn.close()
                continue
                
            # Desempacota: Q = unsigned long long (8), I = unsigned int (4)
            offset_bytes, track_id = struct.unpack('QI', header_data)
            
            print(f"Pedido recebido: Track {track_id} | Offset {offset_bytes}")

            # Busca o arquivo correspondente ao ID pedido
            base_dir = os.path.dirname(__file__)
            arquivo_atual = fila_manager.obter_arquivo_por_track_id(track_id)
            arquivo_atual = os.path.join(base_dir,"transcoded_files", arquivo_atual)

            print(os.path.exists(arquivo_atual))

            if not arquivo_atual or not os.path.exists(arquivo_atual):
                print(f"ERRO: Track {track_id} ({arquivo_atual}) não disponível.")
                conn.close()
                servidor.close()
                continue

            print(f"Transcrevendo: {arquivo_atual}")
            wf = wave.open(arquivo_atual, 'rb')

            # --- Lógica de Seek (Resume) ---
            if offset_bytes > 0:
                frame_size = wf.getnchannels() * wf.getsampwidth()
                wf.setpos(min(offset_bytes // frame_size, wf.getnframes()))
            
            # --- Enviar Metadados ---
            metadados = {
                'channels': wf.getnchannels(),
                'rate': wf.getframerate(),
                'width': wf.getsampwidth(),
                'filesize': wf.getnframes() * wf.getnchannels() * wf.getsampwidth(),
                'chunk': CHUNK
            }
            json_str = json.dumps(metadados).encode('utf-8')
            conn.sendall(struct.pack('Q', len(json_str)))
            conn.sendall(json_str)

            # --- Enviar Áudio ---
            data = wf.readframes(CHUNK)
            while data:
                conn.sendall(data)
                data = wf.readframes(CHUNK)
            
            wf.close()
            print(f"Envio de '{arquivo_atual}' concluído.")

            # Delay para garantir flush de rede
            time.sleep(2.0)

        except (ConnectionResetError, BrokenPipeError):
            print("Conexão interrompida (Troca de faixa ou queda).")
        except Exception as e:
            print(f"Erro no envio: {e}")
        finally:
            conn.close()
            servidor.close()
            time.sleep(0.5)

if __name__ == "__main__":
    iniciar_servidor()