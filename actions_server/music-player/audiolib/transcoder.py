import subprocess
import sys
import os
import argparse

def verificar_ffmpeg():
    """Verifica se o FFmpeg está instalado e acessível."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def converter_para_redbook(arquivo_entrada, arquivo_saida=None):
    """
    Transcodifica um arquivo de áudio para o padrão Red Book (CD-DA):
    - 44.1 kHz
    - 16-bit PCM (Signed Little Endian)
    - Stereo
    """
    
    # Se não for definido nome de saída, usa o mesmo nome com extensão .wav
    if not arquivo_saida:
        base, _ = os.path.splitext(arquivo_entrada)
        arquivo_saida = f"{base}_redbook.wav"

    # Verifica se o arquivo de entrada existe
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
        return

    print(f"Convertendo '{arquivo_entrada}' para padrão Red Book...")

    # Comando FFmpeg
    # -i: Entrada
    # -c:a pcm_s16le: Codec de áudio PCM 16-bit signed little-endian
    # -ar 44100: Taxa de amostragem de áudio 44.1kHz
    # -ac 2: Canais de áudio (Estéreo)
    # -y: Sobrescrever arquivo de saída se existir sem perguntar
    # -hide_banner -loglevel error: Reduz a verbosidade do ffmpeg (limpa o terminal)
    comando = [
        "ffmpeg",
        "-i", arquivo_entrada,
        "-c:a", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        arquivo_saida
    ]

    try:
        subprocess.run(comando, check=True)
        print(f"✅ Sucesso! Arquivo salvo em: {arquivo_saida}")
        
        # Opcional: Mostrar detalhes do arquivo gerado para confirmação
        tamanho = os.path.getsize(arquivo_saida) / (1024 * 1024)
        print(f"   Tamanho: {tamanho:.2f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante a conversão do FFmpeg.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    # Configuração dos argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Converte áudio para o padrão CD Red Book (44.1kHz, 16bit, Stereo).")
    parser.add_argument("entrada", help="Caminho do arquivo de áudio original")
    parser.add_argument("-o", "--saida", help="Caminho do arquivo de saída (opcional)", default=None)

    args = parser.parse_args()

    if verificar_ffmpeg():
        converter_para_redbook(args.entrada, args.saida)
    else:
        print("Erro Crítico: O FFmpeg não foi encontrado no sistema.")
        print("Por favor, instale o FFmpeg e adicione-o ao PATH.")