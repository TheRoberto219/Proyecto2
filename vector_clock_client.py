import socket
import time
import random
import json

class VectorClockClient:
    def __init__(self, server_port, process_id, total_processes):
        """Inicializa el cliente con:
        - server_port: Puerto del servidor
        - process_id: Identificador único (1 para cliente)
        - total_processes: Número total de procesos"""
        self.server_port = server_port
        self.process_id = process_id
        self.total_processes = total_processes
        self.vector_clock = [0] * total_processes  # Reloj vectorial inicializado en ceros
        
    def internal_event(self):
        """Evento interno: Incrementa solo su propio contador"""
        self.vector_clock[self.process_id] += 1
        print(f"\n[Cliente {self.process_id}] Evento interno")
        print(f"[Cliente {self.process_id}] Vector actualizado: {self.vector_clock}")

    def send_message(self):
        """Envía un mensaje al servidor:
        1. Incrementa su contador
        2. Serializa y envía su vector"""
        self.vector_clock[self.process_id] += 1
        print(f"\n[Cliente {self.process_id}] Preparando mensaje")
        print(f"[Cliente {self.process_id}] Vector actual: {self.vector_clock}")
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', self.server_port))
            s.send(json.dumps(self.vector_clock).encode())  # Serializa el vector a JSON
            print(f"[Cliente {self.process_id}] Mensaje enviado")
            s.close()
        except Exception as e:
            print(f"[Cliente {self.process_id}] Error al conectar: {e}")

    def simulate(self, num_events):
        """Simula eventos aleatorios:
        - num_events: Número total de eventos a generar"""
        print(f"[Cliente {self.process_id}] Iniciando simulación...")
        for _ in range(num_events):
            time.sleep(random.randint(1, 3))  # Espera aleatoria entre eventos
            action = random.choice(["interno", "enviar"])
            if action == "interno":
                self.internal_event()
            else:
                self.send_message()
        print(f"[Cliente {self.process_id}] Simulación completada")


    
client = VectorClockClient(9099, 1, 2)
client.simulate(5)  # Genera 5 eventos aleatorios