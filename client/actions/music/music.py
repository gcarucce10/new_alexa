import subprocess
import threading
import re
import time
import select

# --- Variáveis de Estado ---
ffmpeg_process = None
ffplay_process = None
current_time_seconds = 0.0
is_playing = False
lock = threading.Lock() # Para acesso seguro à variável de tempo

# --- Configurações ---
FILE_PATH = r"C:\Caminho\Para\Seu\Arquivo.flac"
SERVER_IP = "127.0.0.1" # Mude para seu IP se o cliente for remoto
PORT = "1234"

# --- Regex para pegar o tempo do ffmpeg ---
TIME_REGEX = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})")

def parse_time(time_str):
    """Converte HH:MM:SS.ms para segundos."""
    match = TIME_REGEX.search(time_str)
    if match:
        h, m, s, ms = map(int, match.groups())
        return h * 3600 + m * 60 + s + ms / 100.0
    return None

def read_ffmpeg_output(process):
    """Lê stderr do ffmpeg em uma thread e atualiza o tempo."""
    global current_time_seconds
    # Usamos select para ler de forma não-bloqueante (melhor em Linux/macOS)
    # Para Windows, a leitura direta pode funcionar mas pode bloquear.
    # Uma abordagem mais robusta pode ser necessária em produção.
    try:
        while process.poll() is None: # Enquanto o processo estiver rodando
            line = process.stderr.readline()
            if not line:
                break
            line = line.decode('utf-8', errors='ignore').strip()
            # FFMPEG imprime o progresso com '\r' no final, então pegamos essas linhas
            if 'time=' in line:
                # print(f"Debug FFMPEG: {line}") # Descomente para depurar
                t = parse_time(line)
                if t is not None:
                    with lock:
                        current_time_seconds = t
            time.sleep(0.05) # Pequena pausa para não sobrecarregar a CPU
    except Exception as e:
        print(f"Erro lendo stderr: {e}")
    print("Thread de leitura finalizada.")


def start_stream(start_at=0.0):
    """Inicia ffmpeg e ffplay."""
    global ffmpeg_process, ffplay_process, is_playing, current_time_seconds
    if is_playing:
        print("Já está tocando.")
        return

    print(f"Iniciando stream a partir de {start_at:.2f} segundos...")
    with lock:
        current_time_seconds = start_at

    ffmpeg_command = [
        'ffmpeg', '-hide_banner', # '-v', 'quiet', # Use para menos output, mas pode perder o tempo
        '-ss', str(start_at),
        '-re',
        '-i', FILE_PATH,
        '-c:a', 'libopus',
        '-b:a', '256k',
        '-ar', '48000',
        '-f', 'mpegts',
        f'tcp://{SERVER_IP}:{PORT}'
    ]

    # Inicia ffmpeg capturando stderr
    ffmpeg_process = subprocess.Popen(
        ffmpeg_command,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL
    )
    time.sleep(1) # Dá um tempo pro ffmpeg começar a enviar

    ffplay_command = [
        'ffplay', '-hide_banner', '-autoexit', # '-nodisp', # Se não quiser janela
        f'tcp://0.0.0.0:{PORT}?listen=1'
    ]

    # Inicia ffplay
    ffplay_process = subprocess.Popen(ffplay_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2) # Dá um tempo pro ffplay conectar e começar

    if ffmpeg_process.poll() is None and ffplay_process.poll() is None:
        print("Stream iniciado com sucesso!")
        is_playing = True
        # Inicia a thread para ler o tempo
        thread = threading.Thread(target=read_ffmpeg_output, args=(ffmpeg_process,), daemon=True)
        thread.start()
    else:
        print("Falha ao iniciar stream.")
        stop_stream()


def stop_stream():
    """Para ffmpeg e ffplay."""
    global ffmpeg_process, ffplay_process, is_playing
    if not is_playing:
        print("Não está tocando.")
        return

    print("Parando stream...")
    if ffplay_process:
        ffplay_process.terminate()
        ffplay_process.wait(timeout=2) # Espera um pouco
        if ffplay_process.poll() is None: # Se não terminou
           ffplay_process.kill() # Força
        ffplay_process = None

    if ffmpeg_process:
        ffmpeg_process.terminate()
        ffmpeg_process.wait(timeout=2)
        if ffmpeg_process.poll() is None:
           ffmpeg_process.kill()
        ffmpeg_process = None

    is_playing = False
    print("Stream parado.")
    with lock:
      print(f"Último tempo registrado: {current_time_seconds:.2f} segundos.")


# --- Loop de Controle Principal ---
try:
    while True:
        command = input("Digite 'play', 'pause', 'quit': ").strip().lower()
        if command == 'play':
            if not is_playing:
                start_stream(current_time_seconds)
            else:
                print("Já está tocando.")
        elif command == 'pause':
            if is_playing:
                stop_stream()
            else:
                print("Não está tocando para pausar.")
        elif command == 'quit':
            if is_playing:
                stop_stream()
            break
        else:
            print("Comando inválido.")

except KeyboardInterrupt:
    print("\nSaindo...")
    if is_playing:
        stop_stream()