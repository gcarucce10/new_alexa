import sys
import os
import gerenciador_fila
import argparse

def encontrar_musicas_album(pasta_raiz, nome_artista, nome_album):
    """Encontra músicas (esta função poderia estar num módulo partilhado também)."""
    caminho_album = os.path.join(pasta_raiz, nome_artista, nome_album)
    if not os.path.isdir(caminho_album):
        return []
    
    # Usamos os.path.abspath para garantir que temos o caminho completo e inequívoco
    return [os.path.abspath(os.path.join(caminho_album, f)) 
            for f in sorted(os.listdir(caminho_album)) 
            if f.lower().endswith(('.mp3', '.flac', '.wav', '.aac'))]

def main_controlador():

    parser = argparse.ArgumentParser(description='Reprodutor de Músicas.')    

    parser.add_argument(
        '--option',
        type=str,
        choices=['play', 'next', 'stop'],
        help='A ação a ser executada: play, next ou stop.'
    )

    parser.add_argument(
        '--type',
        type=str,
        choices=['album'],
        help='O tipo de conteúdo a ser reproduzido (ex: album).'
    )

    parser.add_argument(
        '--artist',
        type=str,
        help='O nome do artista do álbum.'
    )

    parser.add_argument(
        '--album',
        type=str,
        help='O nome do álbum a ser reproduzido.'
    )

    args = parser.parse_args()

    

    if not args:
        print("Uso: python controlador.py [play album <artista> <album> | next | stop]")
        return
    
    path_music = os.path.join("F:\\", "Midioteca", "Musica")

    acao = args.option

    if acao == 'play' and args.type == 'album' and args.artist and args.album:
        nome_artista = args.artist
        nome_album = args.album
        print(f"A procurar pelo álbum '{nome_album}' de '{nome_artista}'...")
        musicas = encontrar_musicas_album(path_music, nome_artista, nome_album)
        if not musicas:
            print("Álbum não encontrado ou sem músicas válidas.")
            return
            
        dados_para_escrever = {'fila': musicas}
        gerenciador_fila.escrever_fila(dados_para_escrever)
        print(f"{len(musicas)} músicas adicionadas à fila. O reprodutor irá começar a tocar.")

    elif acao == 'next':
        dados_atuais = gerenciador_fila.ler_fila()
        if dados_atuais['fila']:
            musica_removida = dados_atuais['fila'].pop(0)
            gerenciador_fila.escrever_fila(dados_atuais)
            print(f"Comando 'next' enviado. Removido: {os.path.basename(musica_removida)}")
        else:
            print("A fila já está vazia.")

    elif acao == 'stop':
        gerenciador_fila.escrever_fila({'fila': []})
        print("Comando 'stop' enviado. A fila de reprodução foi limpa.")

    else:
        print(f"Comando '{acao}' desconhecido.")
        print("Uso: python controlador.py [play album <artista> <album> | next | stop]")

if __name__ == '__main__':
    main_controlador()