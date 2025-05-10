import socket
import time
import random

reloj_logico = 0

def evento_interno():
    global reloj_logico
    reloj_logico += 1
    print(f"[Cliente] Evento interno. Reloj lógico: {reloj_logico}")

def enviar_mensaje():
    global reloj_logico
    reloj_logico += 1
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 9099))
        s.send(str(reloj_logico).encode())
        print(f"[Cliente] Enviando mensaje con reloj {reloj_logico}")
        s.close()
    except:
        print("[Cliente] Error al conectar al servidor")

if __name__ == "__main__":
    for _ in range(5):
        time.sleep(random.randint(1, 3))
        accion = random.choice(["interno", "enviar"])
        if accion == "interno":
            evento_interno()
        else:
            enviar_mensaje()
