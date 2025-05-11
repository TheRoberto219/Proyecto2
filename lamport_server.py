import socket
import threading

reloj_logico = 0

def manejar_cliente(conn, addr):
    global reloj_logico
    print(f"\n[Servidor] Conexión entrante de {addr} | Reloj actual: {reloj_logico}")
    
    reloj_remoto = int(conn.recv(1024).decode())
    print(f"[Servidor] Reloj recibido del cliente: {reloj_remoto}")
    
    reloj_logico = max(reloj_logico, reloj_remoto) + 1
    print(f"[Servidor] Reloj actualizado: {reloj_logico} (max({reloj_logico}, {reloj_remoto}) + 1)")
    
    conn.close()

def iniciar_servidor(puerto):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("localhost", puerto))
    servidor.listen()
    print(f"[Servidor] Escuchando en puerto {puerto}...")

    while True:
        conn, addr = servidor.accept()
        threading.Thread(target=manejar_cliente, args=(conn, addr)).start()

if __name__ == "__main__":
    iniciar_servidor(9099)
