import argparse

from reprodutor import main_reprodutor
from controlador import main_controlador


def main():
    """Função principal para analisar os argumentos e chamar a ação correspondente."""
    parser = argparse.ArgumentParser(description='Reprodutor de Músicas.')

    parser.add_argument(
        '--init',
        type=str,
        choices=['yes', 'no'],
        help='Use para o reprodutor de música.'
    )      

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

    if args.init == 'yes':
        print("Inicializando o reprodutor em segundo plano...")
        main_reprodutor()
        return
    else:
        print("Iniciando o controlador de reprodução de música...")
        main_controlador()

if __name__ == '__main__':
    main()