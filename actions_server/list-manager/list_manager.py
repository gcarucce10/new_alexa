import actions_server
import json
import os
from pathlib import Path

class ListManagerAction(actions_server.ActionsServer):
    def __init__(self):
        super().__init__()
        self.data_file = Path(__file__).resolve().parent / "list_manager_data.json"

    def _load_lists(self) -> dict:
        if self.data_file.exists() and self.data_file.stat().st_size > 0:
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")
                return {}
        return {}

    def _save_lists(self, data: dict):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")

    def perform_action(self, params: dict) -> str:
        # Note que mudei a 'type hint' do retorno para -> str
        mode = params.get('mode')
        list_name = params.get('list')
        item_name = params.get('item')

        data = self._load_lists()
        updated = False
        response_text = ""

        # --- MODO: LISTAR TODAS AS LISTAS ---
        if mode == "list":
            if not data:
                return "Não há listas criadas no momento."
            # Retorna: "Compras, Tarefas, Filmes"
            return ", ".join(data.keys())

        # --- MODO: LISTAR ITENS (LIST-ITEMS) ---
        elif mode == "list-items":
            if not list_name:
                return "Erro: Você precisa dizer o nome da lista."
            
            if list_name in data:
                items = data[list_name]
                if not items:
                    return f"A lista {list_name} está vazia."
                # Retorna: "Tomate, cebola, laranja"
                return ", ".join(items)
            else:
                return f"Não encontrei a lista chamada {list_name}."

        # --- MODO: CRIAR LISTA ---
        elif mode == "create":
            if not list_name:
                return "Erro: Falta o nome da lista para criar."
            
            if list_name in data:
                return f"A lista {list_name} já existe."
            
            data[list_name] = []
            updated = True
            response_text = f"Lista {list_name} criada com sucesso."

        # --- MODO: ADICIONAR ITEM (SAVE) ---
        elif mode == "save":
            if not list_name or not item_name:
                return "Erro: Preciso do nome da lista e do item."

            if list_name not in data:
                data[list_name] = []
                # Opcional: Avisar que criou a lista, mas vamos focar no item
            
            if item_name in data[list_name]:
                return f"O item {item_name} já está na lista {list_name}."
            
            data[list_name].append(item_name)
            updated = True
            response_text = f"Item {item_name} adicionado à lista {list_name}."

        # --- MODO: REMOVER (REMOVE) ---
        elif mode == "remove":
            if not list_name:
                return "Erro: Preciso do nome da lista."

            if list_name not in data:
                return f"A lista {list_name} não existe."

            # Remover Item Específico
            if item_name:
                if item_name in data[list_name]:
                    data[list_name].remove(item_name)
                    updated = True
                    response_text = f"Item {item_name} removido da lista {list_name}."
                else:
                    return f"O item {item_name} não está na lista {list_name}."
            
            # Remover Lista Inteira
            else:
                del data[list_name]
                updated = True
                response_text = f"A lista {list_name} foi removida."

        else:
            return "Erro: Não entendi o modo de operação."

        if updated:
            self._save_lists(data)

        return response_text

if __name__ == "__main__":
    server = ListManagerAction()
    server.flask_server()