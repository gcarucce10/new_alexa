import os
import sys
import json
import socket
import keyboard
import time
import subprocess

# Use full paths (strings) for the files so we can check existence and open them.
BASE_DIR = os.path.dirname(__file__)
ARQUIVO_CONFIG = os.path.join(BASE_DIR, "request.json")
ARQUIVO_AUDIO_QUEUE = os.path.join(BASE_DIR, "lista_reproducao.json")
reciever_process: subprocess.Popen = None

def consume_request():
    """
    Verifica se o ficheiro config existe. Se sim, lê a URL e apaga o ficheiro.
    """
    if not os.path.exists(ARQUIVO_CONFIG):
        return None

    try:
        print("\n[INFO] Novo ficheiro de configuração detetado!")
        with open(ARQUIVO_CONFIG, 'r') as f:
            dados = json.load(f)
            url_servidor: str | None = dados.get('url', None)
            number_of_tracks: int | None = dados.get('num_tracks', None)
            if number_of_tracks:
                number_of_tracks = int(number_of_tracks)
            command: str | None = dados.get('command', None)
        
        os.remove(ARQUIVO_CONFIG)
        print("[INFO] Configuração lida e ficheiro apagado.")
        return url_servidor, number_of_tracks, command
    except Exception as e:
        print(f"[ERRO] Falha ao ler configuração: {e}")
        return None
    

def create_play_queue(request: tuple[str, int]):
    """
    Cria uma lista de reproducao com base no request
    """
    try: 
        with open(ARQUIVO_AUDIO_QUEUE, 'w+', encoding='utf-8') as fp:

            music_list: list[dict] = []
            for i in range(request[1]):
                host, port = request[0].split(":", 1)
                music_list.append({"host": host, "port": port, "track": i + 1})

            playlist = {"url-list": music_list}
            json.dump(playlist, fp)
            print("[INFO] lista_reproducao.json criada!")

    except Exception as e:
        print(f"[ERRO] Falha ao ler configuração: {e}")
        return None
    

def add_music_to_play_queue(request: tuple[str, int]):
    """
    Adiciona musicas a lista de reproducao ja existente
    """

    if not os.path.exists(ARQUIVO_AUDIO_QUEUE):
        print("[ERRO] Era para ter sido invocado a funcao de criacao de fila")
        return None
    
    try: 
        with open(ARQUIVO_AUDIO_QUEUE, 'r+', encoding='utf-8') as fp:
            dados = json.load(fp)

            music_list: list[dict] = dados.get("url-list")
            print(music_list)
            for i in range(len(music_list),len(music_list) + request[1]):
                host, port = request[0].split(":", 1)
                music_list.append({"host": host, "port": port, "track": i + 1}) 

        with open(ARQUIVO_AUDIO_QUEUE, 'w+', encoding='utf-8') as fp:
            playlist = {"url-list": music_list}
            json.dump(playlist, fp)
            # 

    except Exception as e:
        print(f"[ERRO] Falha ao ler configuração: {e}")
        return None



def init_audio_reciever():
    """
    Carrega o reciever de audio quando requisitado...
    """
    global reciever_process
    # Assign the subprocess to the global variable (do not re-annotate here —
    # annotating a global inside a function raises a SyntaxError)
    print([sys.executable, "-u", "audio_reciever.py"])
    reciever_process = subprocess.Popen([sys.executable, "-u", "audio_reciever.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def check_reciever_running() -> bool:
    """Return True if the global receiver subprocess is alive.

    If the subprocess has terminated, clean up the global variable and
    return False.
    """
    global reciever_process
    if reciever_process is None:
        return False

    try:
        # poll() is non-blocking; returns None if still running
        status = reciever_process.poll()
    except Exception:
        # Something went wrong referencing the process — clear it
        reciever_process = None
        return False

    if status is None:
        return True

    # Process finished; consume leftover output and clear the handle
    try:
        # communicate won't block here because poll() returned non-None
        reciever_process.communicate(timeout=0.1)
    except Exception:
        pass

    reciever_process = None
    return False


def stop_audio_reciever():
    """
    Interrompe na força o reciever de audio
    Limpa lista de reprodução
    """
    global reciever_process

    # Use the helper so we don't try to stop a dead but not-cleared process
    if check_reciever_running():
        reciever_process.terminate()
        reciever_process.wait()
        reciever_process = None

        try:
            os.remove(ARQUIVO_AUDIO_QUEUE)
        except Exception as e:
            print(f"[ERRO] Ao apagar fila de reprodução: {e}")
    else:
        print("[ERRO] Programa nao estava ativo")





HOST = 'localhost'
PORTA_ALVO = 6000

def enviar_comando(acao):
    if check_reciever_running():
        """Envia um JSON {'acao': ...} para o player."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mensagem = json.dumps({'acao': acao}).encode('utf-8')
        sock.sendto(mensagem, (HOST, PORTA_ALVO))
        print(f"--> Comando enviado: {acao}")
        sock.close()
    else:
        print("[ERRO] Programa nao estava ativo")


def program_loop():

    while True:

        # Check for new requests
        request = consume_request()

        if request:


            print(request)
            print(request[0:2])

            command = request[2]
            url = request[0]
            num_tracks = request[1]

            if command:
                if command == "play/pause":
                    enviar_comando('pausar_retomar')
                    time.sleep(0.3)
                elif command == "next":
                    enviar_comando('proximo')
                    time.sleep(0.3)
                elif command == "rewind":
                    enviar_comando('anterior')
                    time.sleep(0.3)
                elif command == "send_audio_to_background":
                    enviar_comando('volume_fundo')
                elif command == "restore_audio_volume":
                    enviar_comando('volume_restaurar')
                elif command == "up_volume":
                    enviar_comando('volume_aumentar')
                elif command == "down_volume":
                    enviar_comando('volume_diminuir')
                elif command == "stop":
                    stop_audio_reciever()

            if url is not None and num_tracks is not None:

                if command == "clear":
                    if check_reciever_running():
                        stop_audio_reciever()
                    create_play_queue(request[0:2])
                    init_audio_reciever()
                

                if check_reciever_running():
                    add_music_to_play_queue(request[0:2])
                else:
                    create_play_queue(request[0:2])
                    init_audio_reciever()

if __name__ == '__main__':
    program_loop()
    pass


