import requests
import json
from datetime import datetime, timedelta

url = "http://localhost:5000/perform_action"

# cria uma data que foi há 1 minuto (passado)
past_time = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")

future_time = (datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")

more_future_time = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")

print(f"--- Tentando agendar para: {past_time} ---")

# ADICIONAR PASSADO
data_add = {
    "param": {
        "mode": "add",
        "message": "Teste de Alerta Imediato",
        "time": past_time
    }
}
requests.post(url, json=data_add)
print("1. Lembrete adicionado (no passado).")

# ADICIONAR PRA DAQUI 1 MIN
data_add = {
    "param": {
        "mode": "add",
        "message": "Teste de Alerta 1 MIN",
        "time": future_time
    }
}
requests.post(url, json=data_add)
print("2. Lembrete adicionado para daqui 1 minuto.")

# ADICIONAR PRA DAQUI 5 MIN
data_add = {
    "param": {
        "mode": "add",
        "message": "Teste de Alerta 5 MIN",
        "time": more_future_time
    }
}
requests.post(url, json=data_add)
print("3. Lembrete adicionado para daqui 5 minutos.")

# VERIFICAR 
print("Verificando alertas...")
data_check = {"param": {"mode": "check"}}
response_check = requests.post(url, json=data_check)

alerts = response_check.json().get('triggered_alerts', [])

if alerts:
    print("SUCESSO! Alertas recebidos:")
    for alert in alerts:
        print(f" -> ALARME: {alert['message']} (Era para: {alert['time']})")
else:
    print("Nenhum alerta disparado (algo deu errado ou a hora ainda não chegou).")

'''
# LISTAR
print("Listando lembretes pendentes...")
data_list = {"param": {"mode": "list"}}
response_list = requests.post(url, json=data_list)
pending_reminders = response_list.json().get('reminders', [])
if pending_reminders:
    for rem in pending_reminders:
        print(f" -> PENDENTE: {rem['message']} (Agendado para: {rem['time']})")
else:
    print("Nenhum lembrete pendente.")
'''

