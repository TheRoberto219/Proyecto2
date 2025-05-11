import socket
import threading
import time
import random
import json
from collections import defaultdict

class BullyNode:
    def __init__(self, node_id, port, all_ports):
        self.node_id = node_id
        self.port = port
        self.all_ports = all_ports
        self.leader_id = max(all_ports.keys())  # El líder inicial es el de mayor ID
        self.active = True
        self.election_in_progress = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('localhost', port))
        self.sock.listen(5)
        
        # Iniciar hilo para escuchar mensajes
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
        
        # Simular comportamiento del nodo
        threading.Thread(target=self.node_behavior, daemon=True).start()

    def listen_for_messages(self):
        """Escucha mensajes entrantes de otros nodos"""
        while True:
            conn, addr = self.sock.accept()
            data = conn.recv(1024).decode()
            conn.close()
            
            if data:
                message = json.loads(data)
                self.handle_message(message)

    def handle_message(self, message):
        """Procesa los mensajes recibidos"""
        msg_type = message['type']
        
        if msg_type == 'election':
            self.handle_election(message)
        elif msg_type == 'answer':
            self.handle_answer(message)
        elif msg_type == 'victory':
            self.handle_victory(message)
        elif msg_type == 'ping':
            self.handle_ping(message)

    def send_message(self, dest_port, msg_type):
        """Envía un mensaje a otro nodo"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', dest_port))
            message = {
                'type': msg_type,
                'sender_id': self.node_id,
                'sender_port': self.port
            }
            s.send(json.dumps(message).encode())
            s.close()
        except:
            pass  # El nodo destino puede estar caído

    def start_election(self):
        """Inicia una elección"""
        if self.election_in_progress:
            return
            
        self.election_in_progress = True
        print(f"Nodo {self.node_id} inicia elección")
        
        # Enviar mensajes de elección a nodos con ID mayor
        higher_nodes = False
        for n_id, port in self.all_ports.items():
            if n_id > self.node_id:
                higher_nodes = True
                self.send_message(port, 'election')
        
        # Si no hay nodos con ID mayor, se declara líder
        if not higher_nodes:
            self.declare_victory()

    def handle_election(self, message):
        """Procesa mensaje de elección"""
        print(f"Nodo {self.node_id} recibe elección de {message['sender_id']}")
        
        # Responder al nodo que inició la elección
        self.send_message(message['sender_port'], 'answer')
        
        # Iniciar su propia elección si tiene mayor ID
        if self.node_id > message['sender_id']:
            self.start_election()

    def handle_answer(self, message):
        """Procesa respuesta a mensaje de elección"""
        print(f"Nodo {self.node_id} recibe respuesta de {message['sender_id']}")
        self.election_in_progress = False  # Hay nodos con mayor ID

    def declare_victory(self):
        """Declara victoria en la elección"""
        print(f"\n=== Nodo {self.node_id} se declara LÍDER ===")
        self.leader_id = self.node_id
        self.election_in_progress = False
        
        # Notificar a todos los nodos
        for port in self.all_ports.values():
            if port != self.port:
                self.send_message(port, 'victory')

    def handle_victory(self, message):
        """Procesa mensaje de victoria"""
        print(f"Nodo {self.node_id} reconoce nuevo líder: {message['sender_id']}")
        self.leader_id = message['sender_id']
        self.election_in_progress = False

    def handle_ping(self, message):
        """Responde a ping para verificar actividad"""
        if self.active:
            self.send_message(message['sender_port'], 'answer')

    def check_leader(self):
        """Verifica si el líder está activo"""
        if self.leader_id == self.node_id:  # Soy el líder
            return True
            
        leader_port = self.all_ports.get(self.leader_id)
        if not leader_port:
            return False
            
        try:
            self.send_message(leader_port, 'ping')
            # Esperar respuesta
            time.sleep(1)
            return True
        except:
            return False

    def node_behavior(self):
        """Comportamiento automático del nodo"""
        while True:
            time.sleep(random.randint(5, 10))
            
            if not self.active:
                continue
                
            # Verificar si el líder está activo
            if not self.check_leader():
                print(f"Nodo {self.node_id} detecta líder caído")
                self.start_election()
            
            # Simular falla aleatoria
            if random.random() < 0.1 and self.node_id != self.leader_id:
                self.active = False
                print(f"\n!!! Nodo {self.node_id} ha fallado !!!\n")
                time.sleep(random.randint(10, 20))
                self.active = True
                print(f"\n!!! Nodo {self.node_id} se ha recuperado !!!\n")

def main():
    # Configuración de nodos (ID: puerto)
    nodes_config = {
        1: 5001,
        2: 5002,
        3: 5003,
        4: 5004,
        5: 5005
    }
    
    # Crear nodos
    node_id = int(input("Ingrese ID del nodo a iniciar (1-5): "))
    node = BullyNode(node_id, nodes_config[node_id], nodes_config)
    
    # Mantener el programa corriendo
    while True:
        time.sleep(1)


main()