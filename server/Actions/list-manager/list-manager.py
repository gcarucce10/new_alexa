#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
from pathlib import Path

# Nome do arquivo para armazenar os dados das listas
DATA_FILE = Path(__file__).resolve().parent / "list_manager_data.json"

def carregar_listas():
    """Carrega as listas do arquivo JSON."""
    if DATA_FILE.exists() and DATA_FILE.stat().st_size > 0:
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Aviso: O arquivo de dados '{DATA_FILE}' está corrompido. Iniciando com dados vazios.")
            return {}
        except Exception as e:
            print(f"Erro ao carregar o arquivo de dados '{DATA_FILE}': {e}. Iniciando com dados vazios.")
            return {}
    return {}

def salvar_listas(listas):
    """Salva as listas no arquivo JSON."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(listas, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar os dados em '{DATA_FILE}': {e}")

def criar_lista(nome_lista, listas):
    """Cria uma nova lista."""
    if not nome_lista:
        print("Erro: O nome da lista é obrigatório para criar uma lista.")
        return False
    if nome_lista in listas:
        print(f"A lista '{nome_lista}' já existe.")
        return False
    else:
        listas[nome_lista] = []
        print(f"Lista '{nome_lista}' criada com sucesso.")
        return True

def remover_lista_ou_item(nome_lista, nome_item, listas):
    """Remove uma lista inteira ou um item específico de uma lista."""
    if not nome_lista:
        print("Erro: O nome da lista é obrigatório para remover.")
        return False

    if nome_lista not in listas:
        print(f"Lista '{nome_lista}' não encontrada.")
        return False

    if nome_item:  # Se um item for especificado, remover o item
        if nome_item in listas[nome_lista]:
            listas[nome_lista].remove(nome_item)
            print(f"Item '{nome_item}' removido da lista '{nome_lista}'.")
            # Se a lista ficar vazia após remover o item, pode-se optar por mantê-la ou removê-la.
            # Aqui, vamos manter a lista vazia.
            return True
        else:
            print(f"Item '{nome_item}' não encontrado na lista '{nome_lista}'.")
            return False
    else:  # Se nenhum item for especificado, remover a lista inteira
        del listas[nome_lista]
        print(f"Lista '{nome_lista}' removida com sucesso.")
        return True

def salvar_item(nome_lista, nome_item, listas):
    """Salva um item em uma lista. Cria a lista se não existir."""
    if not nome_lista or not nome_item:
        print("Erro: O nome da lista e o nome do item são obrigatórios para salvar um item.")
        return False

    if nome_lista not in listas:
        # Cria a lista se ela não existir, conforme o comportamento implícito
        # de poder adicionar um item a uma nova lista.
        listas[nome_lista] = []
        print(f"Lista '{nome_lista}' não existia, foi criada.")

    if nome_item in listas[nome_lista]:
        print(f"Item '{nome_item}' já existe na lista '{nome_lista}'.")
        return False
    else:
        listas[nome_lista].append(nome_item)
        print(f"Item '{nome_item}' salvo na lista '{nome_lista}'.")
        return True

def listar_todas_listas(listas):
    """Lista todas as listas existentes."""
    if not listas:
        print("Nenhuma lista encontrada.")
    else:
        print("Listas existentes:")
        for nome_lista in listas:
            print(f"- {nome_lista}")

def listar_itens_lista(nome_lista, listas):
    """Lista todos os itens de uma lista específica."""
    if not nome_lista:
        print("Erro: O nome da lista é obrigatório para listar itens.")
        return

    if nome_lista in listas:
        itens = listas[nome_lista]
        if itens:
            print(f"Itens na lista '{nome_lista}':")
            for item in itens:
                print(f"- {item}")
        else:
            print(f"A lista '{nome_lista}' está vazia.")
    else:
        print(f"Lista '{nome_lista}' não encontrada.")

def main():
    parser = argparse.ArgumentParser(description="Gerenciador de listas de itens.")
    parser.add_argument(
        "--option",
        required=True,
        choices=["list", "list-items", "create", "remove", "save"],
        help="Ação a ser realizada: \n"
             "  list: listar todas as listas\n"
             "  list-items: listar itens de uma lista específica\n"
             "  create: criar uma nova lista\n"
             "  remove: remover uma lista ou um item de uma lista\n"
             "  save: salvar um item em uma lista"
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Nome da lista (assunto) a ser gerenciada."
    )
    parser.add_argument(
        "--item",
        type=str,
        help="Nome do item (usado com --option save ou --option remove para remover um item específico)."
    )

    args = parser.parse_args()
    listas = carregar_listas()
    alteracao_feita = False

    if args.option == "list":
        listar_todas_listas(listas)
    elif args.option == "list-items":
        if not args.name:
            parser.error("--name é obrigatório com --option list-items")
        listar_itens_lista(args.name, listas)
    elif args.option == "create":
        if not args.name:
            parser.error("--name é obrigatório com --option create")
        if criar_lista(args.name, listas):
            alteracao_feita = True
    elif args.option == "remove":
        if not args.name:
            parser.error("--name é obrigatório com --option remove")
        if remover_lista_ou_item(args.name, args.item, listas): # args.item pode ser None
            alteracao_feita = True
    elif args.option == "save":
        if not args.name or not args.item:
            parser.error("--name e --item são obrigatórios com --option save")
        if salvar_item(args.name, args.item, listas):
            alteracao_feita = True
    else:
        print(f"Opção '{args.option}' desconhecida.")
        parser.print_help()

    if alteracao_feita:
        salvar_listas(listas)

if __name__ == "__main__":
    main()