import socket
import threading
import time
import random
import json

class BullyNode:
    def __init__(self, node_id, port, all_ports):
        self.node_id = node_id
        self.port = port
        self.all_ports = all_ports  # {id: port}
        self.leader_id = max(all_ports.keys())
        self.active = True
        self.election_in_progress = False
        self.ok_received = False
        
        # Configurar socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('localhost', port))
        self.sock.listen(5)
        
        # Iniciar hilos
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
        threading.Thread(target=self.node_behavior, daemon=True).start()
        threading.Thread(target=self.print_status, daemon=True).start()

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
            self.handle_ping()

    def send_message(self, dest_port, msg_type):
        """Envía mensaje a otro nodo"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect(('localhost', dest_port))
            message = {
                'type': msg_type,
                'sender_id': self.node_id,
                'sender_port': self.port
            }
            s.send(json.dumps(message).encode())
            s.close()
            return True
        except:
            return False

    def start_election(self):
        """Inicia proceso de elección"""
        if not self.active or self.election_in_progress:
            return
            
        self.election_in_progress = True
        self.ok_received = False
        print(f"\n[Nodo {self.node_id}] Iniciando elección")
        
        # Enviar a nodos con mayor ID
        higher_nodes = [n_id for n_id in self.all_ports if n_id > self.node_id]
        
        for n_id in higher_nodes:
            if self.send_message(self.all_ports[n_id], 'election'):
                print(f"[Nodo {self.node_id}] Enviado ELECTION a {n_id}")
        
        # Esperar respuestas
        time.sleep(2)
        
        # Si no hay nodos mayores o no respondieron
        if not higher_nodes or not self.ok_received:
            self.declare_victory()
        else:
            print(f"[Nodo {self.node_id}] Elección fallida, recibió OK")
            self.election_in_progress = False

    def handle_election(self, message):
        """Procesa mensaje de elección"""
        if not self.active:
            return
            
        print(f"[Nodo {self.node_id}] Recibido ELECTION de {message['sender_id']}")
        
        # Responder OK
        if self.send_message(message['sender_port'], 'answer'):
            print(f"[Nodo {self.node_id}] Enviado ANSWER a {message['sender_id']}")
        
        # Iniciar propia elección si tiene mayor ID
        if self.node_id > message['sender_id']:
            self.start_election()

    def handle_answer(self):
        """Procesa respuesta OK"""
        self.ok_received = True

    def declare_victory(self):
        """Se declara líder"""
        self.leader_id = self.node_id
        self.election_in_progress = False
        print(f"\n=== [Nodo {self.node_id}] ¡Soy el nuevo LÍDER! ===")
        
        # Notificar a todos
        for n_id, port in self.all_ports.items():
            if n_id != self.node_id:
                if self.send_message(port, 'victory'):
                    print(f"[Nodo {self.node_id}] Notificado VICTORY a {n_id}")

    def handle_victory(self, message):
        """Procesa anuncio de victoria"""
        print(f"[Nodo {self.node_id}] Reconociendo nuevo líder: {message['sender_id']}")
        self.leader_id = message['sender_id']
        self.election_in_progress = False

    def handle_ping(self):
        """Responde a ping"""
        if self.active:
            return True
        return False

    def check_leader(self):
        """Verifica si el líder está activo"""
        if self.leader_id == self.node_id:
            return True
            
        leader_port = self.all_ports.get(self.leader_id)
        if not leader_port:
            return False
            
        try:
            return self.send_message(leader_port, 'ping')
        except:
            return False

    def node_behavior(self):
        """Comportamiento automático del nodo"""
        while True:
            # Intervalo aleatorio entre 5-10 segundos
            time.sleep(random.randint(5, 10))
            
            if not self.active:
                continue
                
            # Verificar líder (excepto si soy el líder)
            if self.node_id != self.leader_id:
                if not self.check_leader():
                    print(f"[Nodo {self.node_id}] ¡Líder {self.leader_id} no responde!")
                    self.start_election()
            
            # Simular falla aleatoria (10% de probabilidad, AHORA INCLUYE AL LÍDER)
            if random.random() < 0.1:  # Eliminada la restricción para el líder
                self.active = False
                print(f"\n[Nodo {self.node_id}] ¡HE FALLADO!")
                time.sleep(random.randint(30, 45))
                self.active = True
                print(f"\n[Nodo {self.node_id}] ¡RECUPERADO!")
                # Si era el líder, iniciar elección al recuperarse
                if self.node_id == self.leader_id:
                    self.start_election()

    def print_status(self):
        """Muestra estado periódicamente"""
        while True:
            time.sleep(2)
            if self.active:
                status = "LÍDER" if self.node_id == self.leader_id else f"seguidor (Líder: {self.leader_id})"
                print(f"[Nodo {self.node_id}] Estado: {status}")

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
    
    print(f"\nIniciando nodo {node_id} en puerto {nodes_config[node_id]}")
    print("----------------------------------------")
    
    node = BullyNode(node_id, nodes_config[node_id], nodes_config)
    
    # Mantener programa ejecutando
    while True:
        time.sleep(1)

main()
