import socket
import threading
import json

class VectorClockServer:
    def __init__(self, port, process_id, total_processes):
        """Inicializa el servidor con:
        - port: Puerto de escucha
        - process_id: Identificador único del proceso (0 para servidor)
        - total_processes: Número total de procesos en el sistema"""
        self.port = port
        self.process_id = process_id
        self.total_processes = total_processes
        self.vector_clock = [0] * total_processes  # Inicializa el reloj vectorial
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def update_vector_clock(self, received_vector):
        """Actualiza el reloj vectorial al recibir un mensaje:
        1. Incrementa su propio contador
        2. Actualiza cada posición con el máximo entre su valor y el recibido"""
        print(f"\n[Servidor {self.process_id}] Vector recibido: {received_vector}")
        print(f"[Servidor {self.process_id}] Vector actual antes de actualizar: {self.vector_clock}")
        
        # Regla de actualización de relojes vectoriales
        self.vector_clock[self.process_id] += 1  # Paso 1: Incremento local
        for i in range(self.total_processes):
            self.vector_clock[i] = max(self.vector_clock[i], received_vector[i])  # Paso 2: Actualización por máximos
            
        print(f"[Servidor {self.process_id}] Vector actualizado: {self.vector_clock}")

    def handle_client(self, conn, addr):
        """Maneja la conexión entrante:
        1. Recibe el vector del cliente
        2. Actualiza su reloj vectorial"""
        data = conn.recv(1024).decode()
        received_vector = json.loads(data)  # Deserializa el vector recibido
        self.update_vector_clock(received_vector)
        conn.close()

    def start(self):
        """Inicia el servidor en el puerto configurado"""
        self.server_socket.bind(('localhost', self.port))
        self.server_socket.listen()
        print(f"[Servidor {self.process_id}] Escuchando en puerto {self.port}...")
        
        while True:
            conn, addr = self.server_socket.accept()
            # Maneja cada conexión en un hilo separado
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def internal_event(self):
        """Simula un evento interno incrementando su propio contador"""
        self.vector_clock[self.process_id] += 1
        print(f"\n[Servidor {self.process_id}] Evento interno")
        print(f"[Servidor {self.process_id}] Vector actualizado: {self.vector_clock}")


    
server = VectorClockServer(9099, 0, 2)
server.start()