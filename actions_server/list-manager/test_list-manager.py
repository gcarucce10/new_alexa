import requests
import argparse
import sys
import json

parser = argparse.ArgumentParser(description="Teste do List Manager (Retorno em String)")
parser.add_argument("--mode", required=True, choices=["create", "remove", "save", "list", "list-items"])
parser.add_argument("--list", help="Nome da lista")
parser.add_argument("--item", help="Nome do item")

args = parser.parse_args()

url = "http://localhost:5000/perform_action"

data_payload = {
    "param": {
        "mode": args.mode,
        "list": args.list,
        "item": args.item
    }
}

try:
    print(f"--- Enviando comando: {args.mode} ---")
    response = requests.post(url, json=data_payload)
    
    print(f"Status: {response.status_code}")
    
    # Como agora retorna uma string direta (dentro do JSON do flask), imprimimos direto
    print(f" -> \"{response.json()}\"")

except requests.exceptions.ConnectionError:
    print("ERRO: Não foi possível conectar ao servidor.")
except Exception as e:
    print(f"Erro inesperado: {e}")