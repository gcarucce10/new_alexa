import argparse
import json
import time
import os
from datetime import datetime

# Tenta importar a biblioteca de notificação. Se não conseguir, avisa o usuário.
try:
    from plyer import notification
    PLYER_DISPONIVEL = True
except ImportError:
    PLYER_DISPONIVEL = False

# Nome do arquivo para armazenar os lembretes
REMINDERS_FILE = os.path.join("actions", "reminder", "reminders.json")

def carregar_lembretes():
    """Carrega os lembretes do arquivo JSON."""
    try:
        with open(REMINDERS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def salvar_lembretes(lembretes):
    """Salva a lista de lembretes no arquivo JSON."""
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(lembretes, f, indent=4)

def criar_lembrete(nome, tempo_str):
    """Cria e armazena um novo lembrete."""
    if not nome or not tempo_str:
        print("Erro: Para criar um lembrete, são necessários o nome e o tempo.")
        return

    try:
        # Valida o formato da data e hora
        datetime.strptime(tempo_str, '%Y-%m-%d %H:%M')
    except ValueError:
        print("Erro: Formato de data e hora inválido. Use AAAA-MM-DD HH:MM.")
        return

    lembretes = carregar_lembretes()
    
    if any(l['nome'] == nome for l in lembretes):
        print(f"Erro: Um lembrete com o nome '{nome}' já existe.")
        return
        
    novo_lembrete = {'nome': nome, 'tempo': tempo_str}
    lembretes.append(novo_lembrete)
    salvar_lembretes(lembretes)
    print(f"Lembrete '{nome}' criado para {tempo_str}.")

def listar_lembretes():
    """Lista todos os lembretes armazenados."""
    lembretes = carregar_lembretes()
    if not lembretes:
        print("Nenhum lembrete encontrado.")
    else:
        print("Seus lembretes:")
        lembretes_ordenados = sorted(lembretes, key=lambda l: l['tempo'])
        for lembrete in lembretes_ordenados:
            print(f"- {lembrete['nome']} em {lembrete['tempo']}")

def remover_lembrete(nome):
    """Remove um lembrete específico pelo nome."""
    if not nome:
        print("Erro: Para remover um lembrete, é necessário o nome.")
        return

    lembretes = carregar_lembretes()
    lembretes_filtrados = [l for l in lembretes if l['nome'] != nome]

    if len(lembretes) == len(lembretes_filtrados):
        print(f"Erro: Lembrete com o nome '{nome}' não encontrado.")
    else:
        salvar_lembretes(lembretes_filtrados)
        print(f"Lembrete '{nome}' removido com sucesso.")

def monitorar_lembretes():
    """Fica em loop, verificando e disparando alertas para lembretes."""
    global notification
    if not PLYER_DISPONIVEL:
        print("Erro: A biblioteca 'plyer' não foi encontrada.")
        print("Por favor, instale-a com: pip install plyer")
        return

    print("Monitorando lembretes... Pressione Ctrl+C para parar.", flush=True)
    try:
        while True:
            lembretes = carregar_lembretes()
            lembretes_restantes = []
            agora = datetime.now()

            for lembrete in lembretes:
                tempo_lembrete = datetime.strptime(lembrete['tempo'], '%Y-%m-%d %H:%M')
                
                # Se a hora do lembrete já passou ou é agora
                if tempo_lembrete <= agora:
                    print(f"ALERTA: Lembrete '{lembrete['nome']}'!", flush=True)
                    
                    # Dispara a notificação de desktop
                    notification.notify(
                        title='Alerta de Lembrete!',
                        message=f"Está na hora de: {lembrete['nome']}",
                        app_name='Reminder',
                        timeout=10  # A notificação desaparecerá após 10 segundos
                    )
                    # O lembrete já foi disparado, então não o adicionamos de volta à lista
                else:
                    lembretes_restantes.append(lembrete)
            
            # Se algum lembrete foi removido (disparado), salva a nova lista
            if len(lembretes_restantes) != len(lembretes):
                salvar_lembretes(lembretes_restantes)

            # Espera 30 segundos antes de verificar novamente para não usar muita CPU
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado.")

def main():
    """Função principal para analisar os argumentos e chamar a ação correspondente."""
    parser = argparse.ArgumentParser(description='Gerenciador de lembretes de linha de comando.')
    
    parser.add_argument(
        '--option',
        type=str,
        choices=['create', 'list', 'remove', 'monitor'], # Adicionamos 'monitor'
        help='A ação a ser executada: create, list, remove ou monitor.'
    )

    parser.add_argument(
        '--init',
        type=str,
        choices=['yes', 'no'],
        help='Só use se quiser inicializar o monitoramento dos lembretes.'
    )

    parser.add_argument(
        '--name',
        type=str,
        help='O nome do lembrete.'
    )
    parser.add_argument(
        '--time',
        type=str,
        help='A data e hora do lembrete (formato: AAAA-MM-DD HH:MM).'
    )

    args = parser.parse_args()

    if args.init == 'yes':
        print("Inicializando o monitoramento de lembretes...")
        monitorar_lembretes()
        return
    elif args.option == 'create':
        criar_lembrete(args.name, args.time)
    elif args.option == 'list':
        listar_lembretes()
    elif args.option == 'remove':
        remover_lembrete(args.name)
    elif args.option == 'monitor': # Adicionamos a lógica para 'monitor'
        monitorar_lembretes()

if __name__ == '__main__':
    main()