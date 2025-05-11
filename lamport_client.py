import socket
import time
import random

reloj_logico = 0

def evento_interno():
    global reloj_logico
    reloj_logico += 1
    print(f"\n[Cliente] Evento interno | Reloj: {reloj_logico} (+1)")

def enviar_mensaje():
    global reloj_logico
    reloj_logico += 1
    print(f"\n[Cliente] Enviando mensaje | Reloj: {reloj_logico} (+1)")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 9099))
        s.send(str(reloj_logico).encode())
        print(f"[Cliente] Mensaje enviado con reloj: {reloj_logico}")
        s.close()
    except Exception as e:
        print(f"[Cliente] Error al conectar: {e}")


print("[Cliente] Iniciando simulación...")
for i in range(5):
    time.sleep(random.randint(1, 3))
    accion = random.choice(["interno", "enviar"])
    if accion == "interno":
        evento_interno()
    else:
        enviar_mensaje()
print("[Cliente] Simulación completada.")
