from flask import Flask, request, jsonify
import json 
import os
from datetime import datetime

import actions_server

class ReminderAction(actions_server.ActionsServer):
    def __init__(self):
        super().__init__()

        self.db_file = "reminders_db.json"
    

    def _load_reminders(self) -> list:
        """
        Método interno para ler o arquivo de lembretes.
        Se o arquivo não existir, retorna uma lista vazia.
        """
        if not os.path.exists(self.db_file):
            return []
        
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Se o arquivo estiver corrompido, retorna lista vazia para evitar crash
            return []

    def _save_reminders(self, reminders_list: list):
        """
        Método interno para salvar a lista atualizada no arquivo.
        """
        with open(self.db_file, 'w', encoding='utf-8') as f:
            # indent=4 deixa o arquivo bonitinho para humanos lerem
            json.dump(reminders_list, f, indent=4, ensure_ascii=False)

    def perform_action(self, params: dict) -> tuple[dict, dict]:

        mode = params.get('mode')
        # Carrega a lista atual do arquivo
        reminders = self._load_reminders()  
        self.list_reminder = self.check_reminders()      

        # --- MODO: ADICIONAR (ADD) ---
        if mode == "add":

            message = params.get('message')
            time_str = params.get('time') 


            if not message or not time_str:
                return {"error": "Faltam parâmetros: 'message' ou 'time' são obrigatórios."}


            # Cria o novo objeto lembrete
            new_reminder = {
                "message": message,
                "time": time_str,
                "status": "pending"  # Marcamos como pendente para saber que não foi notificado ainda
            }

            # Adiciona na lista e salva no arquivo
            reminders.append(new_reminder)
            self._save_reminders(reminders)

            return [{"result": f"Lembrete agendado: '{message}' para {time_str}"},
                   {"resource": 
                    {
                        "name": "reminder",
                        "config": {
                        "url": os.getenv("IP", "0.0.0.0") + ":" + os.getenv("PORT", 5000)
                        }
                    } 
                  }]

        # --- MODO: LISTAR (LIST) ---
        elif mode == "list":
            # Retorna apenas os pendentes 
            pending_list = [r for r in reminders if r['status'] == 'pending']
            result = ""
            for r in pending_list:
                result = result + f"Lembrete pendente: {r['message']} às {r['time']}\n"
            return [{"result": result}, {}]

        else:
            return {"error": f"Modo '{mode}' não reconhecido."}
        
    def get_reminders(self) -> list:
        """
        Método público para verificar lembretes disparados.
        Retorna a lista dos lembretes atualizada.
        """

        triggered = []
        now = datetime.now()
        updated = False
    
        reminders = self._load_reminders()  

        # Update reminders status if triggered
        for item in reminders:
            # Só verifica se estiver pendente
            if item['status'] == 'pending':
                try:
                    # Converte a string de hora para objeto de data
                    item_time = datetime.strptime(item['time'], "%Y-%m-%d %H:%M")
                    
                    # Se a hora atual é maior ou igual à hora do lembrete
                    if now >= item_time:
                        item['status'] = 'sent' # Marca como enviado
                        triggered.append(item)
                        updated = True
                except ValueError:
                    print(f"Erro ao ler data: {item['time']}")
                    continue
        
        return reminders



if __name__ == "__main__":
    reminder_server = ReminderAction()
    reminder_server.flask_server()