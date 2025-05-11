import socket
import threading
import time
import json
from collections import defaultdict
from queue import Queue

class Process:
    def __init__(self, pid, ports, all_ports):
        self.pid = pid  # Identificador único del proceso
        self.ports = ports  # Puertos de todos los procesos
        self.all_ports = all_ports  # Todos los puertos en el sistema
        self.clock = 0  # Reloj lógico de Lamport
        self.deferred = []  # Solicitudes diferidas
        self.requesting = False  # Indica si está solicitando el recurso
        self.ok_received = 0  # Contador de OKs recibidos
        self.total_processes = len(all_ports)
        self.queue = Queue()  # Cola para manejar mensajes entrantes
        
        # Inicializar el socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', ports[pid]))
        self.sock.listen()
        
        # Iniciar hilo para escuchar mensajes
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
        threading.Thread(target=self.process_messages, daemon=True).start()

    def listen_for_messages(self):
        """Escucha continuamente mensajes entrantes"""
        while True:
            conn, addr = self.sock.accept()
            data = conn.recv(1024).decode()
            conn.close()
            self.queue.put(json.loads(data))

    def process_messages(self):
        """Procesa los mensajes recibidos"""
        while True:
            if not self.queue.empty():
                message = self.queue.get()
                self.handle_message(message)

    def handle_message(self, message):
        """Maneja los diferentes tipos de mensajes"""
        msg_type = message['type']
        self.clock = max(self.clock, message['clock']) + 1
        
        if msg_type == 'request':
            self.handle_request(message)
        elif msg_type == 'ok':
            self.handle_ok()
        elif msg_type == 'release':
            self.handle_release()

    def handle_request(self, message):
        """Procesa una solicitud de otro proceso"""
        their_pid = message['pid']
        their_clock = message['clock']
        
        # Reglas del algoritmo:
        # 1. Si no estoy solicitando o ya tengo el recurso
        # 2. Si su solicitud es anterior (menor timestamp o mismo timestamp pero PID menor)
        should_defer = (self.requesting and 
                       ((their_clock < self.clock) or 
                        (their_clock == self.clock and their_pid < self.pid)))
        
        if should_defer:
            print(f"Proceso {self.pid}: Diferiendo solicitud de {their_pid}")
            self.deferred.append(their_pid)
        else:
            print(f"Proceso {self.pid}: Enviando OK a {their_pid}")
            self.send_message(their_pid, 'ok')

    def handle_ok(self):
        """Procesa un mensaje OK recibido"""
        self.ok_received += 1
        print(f"Proceso {self.pid}: Recibió OK ({self.ok_received}/{self.total_processes-1})")
        
        if self.ok_received == self.total_processes - 1:
            self.access_resource()

    def handle_release(self):
        """Procesa un mensaje de liberación"""
        if self.deferred:
            next_pid = self.deferred.pop(0)
            print(f"Proceso {self.pid}: Enviando OK diferido a {next_pid}")
            self.send_message(next_pid, 'ok')

    def send_message(self, dest_pid, msg_type):
        """Envía un mensaje a otro proceso"""
        self.clock += 1
        message = {
            'type': msg_type,
            'pid': self.pid,
            'clock': self.clock
        }
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', self.ports[dest_pid]))
            s.send(json.dumps(message).encode())
            s.close()
        except Exception as e:
            print(f"Error enviando mensaje a {dest_pid}: {e}")

    def request_resource(self):
        """Solicita acceso al recurso compartido"""
        if self.requesting:
            return
            
        self.requesting = True
        self.ok_received = 0
        self.clock += 1
        
        print(f"\nProceso {self.pid}: Solicitando recurso (ts={self.clock})")
        
        # Enviar solicitud a todos los demás procesos
        for pid in range(self.total_processes):
            if pid != self.pid:
                self.send_message(pid, 'request')

    def access_resource(self):
        """Accede al recurso compartido"""
        print(f"\n=== Proceso {self.pid} ENTRANDO a la sección crítica ===")
        time.sleep(2)  # Simular trabajo en la sección crítica
        print(f"=== Proceso {self.pid} SALIENDO de la sección crítica ===\n")
        self.release_resource()

    def release_resource(self):
        """Libera el recurso compartido"""
        self.requesting = False
        self.clock += 1
        
        # Enviar mensaje de liberación a procesos diferidos
        for pid in self.deferred:
            self.send_message(pid, 'ok')
        self.deferred.clear()
        
        # Notificar a todos que ha liberado el recurso
        for pid in range(self.total_processes):
            if pid != self.pid:
                self.send_message(pid, 'release')

    def simulate(self):
        """Simula el comportamiento del proceso"""
        while True:
            time.sleep(5)  # Esperar antes de hacer otra solicitud
            self.request_resource()


# Configuración: lista de puertos para cada proceso
ports = [5000, 5001, 5002]  # Puertos para 3 procesos
    
# Obtener el ID del proceso del argumento de línea de comandos
import sys
pid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    
process = Process(pid, ports, ports)
process.simulate()