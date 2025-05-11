import socket
import threading
import time
import random
import json

class BullyNode:
    def __init__(self, node_id, port, all_ports):
        self.node_id = node_id
        self.port = port
        self.all_ports = all_ports  # Diccionario {id: puerto}
        self.leader_id = max(all_ports.keys())  # Líder inicial es el de mayor ID
        self.active = True
        self.election_in_progress = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('localhost', port))
        self.sock.listen(5)
        
        # Iniciar hilos
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
        threading.Thread(target=self.node_behavior, daemon=True).start()

    def listen_for_messages(self):
        """Escucha mensajes entrantes"""
        while True:
            try:
                conn, addr = self.sock.accept()
                data = conn.recv(1024).decode()
                conn.close()
                if data:
                    message = json.loads(data)
                    self.handle_message(message)
            except:
                pass

    def handle_message(self, message):
        """Procesa mensajes recibidos"""
        msg_type = message['type']
        
        if msg_type == 'election':
            self.handle_election(message)
        elif msg_type == 'answer':
            self.handle_answer()
        elif msg_type == 'victory':
            self.handle_victory(message)
        elif msg_type == 'ping':
            self.handle_ping(message)

    def send_message(self, dest_port, msg_type):
        """Envía mensaje a otro nodo"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect(('localhost', dest_port))
            message = {
                'type': msg_type,
                'sender_id': self.node_id,
                'sender_port': self.port
            }
            s.send(json.dumps(message).encode())
            s.close()
        except:
            pass

    def start_election(self):
        """Inicia proceso de elección"""
        if self.election_in_progress or not self.active:
            return
            
        self.election_in_progress = True
        print(f"[Nodo {self.node_id}] Inicia elección")
        
        # Enviar a nodos con mayor ID
        higher_nodes = False
        for n_id, port in self.all_ports.items():
            if n_id > self.node_id:
                higher_nodes = True
                self.send_message(port, 'election')
        
        # Esperar respuestas
        time.sleep(3)
        
        # Si no hay nodos mayores o no respondieron
        if not higher_nodes or self.election_in_progress:
            self.declare_victory()

    def handle_election(self, message):
        """Procesa mensaje de elección"""
        if not self.active:
            return
            
        print(f"[Nodo {self.node_id}] Recibe elección de {message['sender_id']}")
        self.send_message(message['sender_port'], 'answer')
        
        # Iniciar su propia elección si tiene mayor ID
        if self.node_id > message['sender_id']:
            self.start_election()

    def handle_answer(self):
        """Procesa respuesta a elección"""
        self.election_in_progress = False

    def declare_victory(self):
        """Se declara líder"""
        print(f"\n=== Nodo {self.node_id} se declara LÍDER ===")
        self.leader_id = self.node_id
        self.election_in_progress = False
        
        # Notificar a todos
        for n_id, port in self.all_ports.items():
            if n_id != self.node_id:
                self.send_message(port, 'victory')

    def handle_victory(self, message):
        """Procesa anuncio de victoria"""
        print(f"[Nodo {self.node_id}] Reconoce nuevo líder: {message['sender_id']}")
        self.leader_id = message['sender_id']
        self.election_in_progress = False

    def handle_ping(self, message):
        """Responde a ping de verificación"""
        if self.active and not self.election_in_progress:
            self.send_message(message['sender_port'], 'answer')

    def check_leader(self):
        """Verifica si el líder está activo"""
        if self.leader_id == self.node_id:
            return True
            
        leader_port = self.all_ports.get(self.leader_id)
        if not leader_port:
            return False
            
        try:
            self.send_message(leader_port, 'ping')
            return True
        except:
            return False

    def node_behavior(self):
        """Comportamiento automático del nodo"""
        while True:
            time.sleep(random.randint(10, 15))  # Verificación menos frecuente
            
            if not self.active:
                continue
                
            # Verificar líder solo si no soy yo
            if self.node_id != self.leader_id:
                if not self.check_leader():
                    print(f"[Nodo {self.node_id}] Detecta líder caído")
                    self.start_election()
            
            # Simular falla aleatoria (no líderes)
            if random.random() < 0.05 and self.node_id != self.leader_id:
                self.active = False
                print(f"[Nodo {self.node_id}] Ha fallado")
                time.sleep(random.randint(15, 25))  # Tiempo de recuperación más largo
                self.active = True
                print(f"[Nodo {self.node_id}] Se ha recuperado")

def main():
    # Configuración de nodos
    nodes_config = {
        1: 5001,
        2: 5002,
        3: 5003,
        4: 5004,
        5: 5005
    }
    
    node_id = int(input("Ingrese ID del nodo (1-5): "))
    if node_id not in nodes_config:
        print("ID inválido")
        return
    
    node = BullyNode(node_id, nodes_config[node_id], nodes_config)
    
    # Mantener programa ejecutando
    while True:
        time.sleep(1)

main()
