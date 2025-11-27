import socket
import json
import keyboard
import time

HOST = 'localhost'
PORTA_ALVO = 6000

def enviar_comando(acao):
    """Envia um JSON {'acao': ...} para o player."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mensagem = json.dumps({'acao': acao}).encode('utf-8')
    sock.sendto(mensagem, (HOST, PORTA_ALVO))
    print(f"--> Comando enviado: {acao}")
    sock.close()

print("--- Controlador Simulado (Cérebro da Alexa) ---")
print("Este script simula o módulo de voz enviando ordens.")
print("Use as teclas para enviar os comandos via REDE:")
print("[P] Pausar/Retomar")
print("[Seta Dir] Próximo")
print("[Seta Esq] Anterior")
print("[ESC] Sair do controlador")

while True:
    if keyboard.is_pressed('p'):
        enviar_comando('pausar_retomar')
        time.sleep(0.3)
    
    if keyboard.is_pressed('right'):
        enviar_comando('proximo')
        time.sleep(0.3)
        
    if keyboard.is_pressed('left'):
        enviar_comando('anterior')
        time.sleep(0.3)

    if keyboard.is_pressed('q'):
        enviar_comando('volume_fundo')
        time.sleep(0.3)
    
    if keyboard.is_pressed('w'):
        enviar_comando('volume_restaurar')
        time.sleep(0.3)
    
    if keyboard.is_pressed('e'):
        enviar_comando('volume_aumentar')
        time.sleep(0.3)

    if keyboard.is_pressed('r'):
        enviar_comando('volume_diminuir')
        time.sleep(0.3)
        
    if keyboard.is_pressed('esc'):
        break

    
    time.sleep(0.05)