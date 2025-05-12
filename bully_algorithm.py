import socket
import threading
import time

class BullyNode:
    def __init__(self, node_id, port, nodes_config):
        self.node_id = node_id
        self.port = port
        self.nodes_config = nodes_config
        self.leader_id = None
        self.state = "follower"
        self.alive = True

        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        time.sleep(2)
        self.start_election()

        # Simulación de fallos y recuperación
        threading.Thread(target=self.failure_simulation).start()

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('localhost', self.port))
            while True:
                try:
                    data, addr = s.recvfrom(1024)
                    message = data.decode()
                    self.handle_message(message)
                except:
                    continue

    def send_message(self, target_id, message):
        port = self.nodes_config[target_id]
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message.encode(), ('localhost', port))

    def broadcast_message(self, message, exclude_self=True):
        for nid in self.nodes_config:
            if exclude_self and nid == self.node_id:
                continue
            self.send_message(nid, message)

    def handle_message(self, message):
        parts = message.split()
        cmd = parts[0]

        if cmd == "ELECTION":
            sender = int(parts[1])
            if self.alive:
                print(f"[Nodo {self.node_id}] Recibido ELECTION de {sender}")
                if self.node_id > sender:
                    self.send_message(sender, f"ANSWER {self.node_id}")
                    print(f"[Nodo {self.node_id}] Enviado ANSWER a {sender}")
                    self.start_election()

        elif cmd == "ANSWER":
            sender = int(parts[1])
            print(f"[Nodo {self.node_id}] Recibido ANSWER de {sender}")
            self.got_answer = True

        elif cmd == "VICTORY":
            new_leader = int(parts[1])
            print(f"[Nodo {self.node_id}] Recibido VICTORY de {new_leader}, mi líder actual es {self.leader_id}")
            if self.leader_id is None or new_leader > self.leader_id:
                self.leader_id = new_leader
                self.state = "follower"
                print(f"[Nodo {self.node_id}] Estado: {self.state} (Líder: {self.leader_id})")

    def start_election(self):
        if not self.alive:
            return

        print(f"[Nodo {self.node_id}] Iniciando elección")
        self.got_answer = False
        for nid in self.nodes_config:
            if nid > self.node_id:
                self.send_message(nid, f"ELECTION {self.node_id}")

        time.sleep(2)

        if not self.got_answer:
            # Soy el nuevo líder
            self.state = "leader"
            self.leader_id = self.node_id
            print(f"=== [Nodo {self.node_id}] ¡Soy el nuevo LÍDER! ===")
            self.broadcast_message(f"VICTORY {self.node_id}")

        else:
            print(f"[Nodo {self.node_id}] Esperando nuevo líder...")

    def failure_simulation(self):
        while True:
            time.sleep(10)
            self.alive = False
            print(f"[Nodo {self.node_id}] ¡HE FALLADO!")
            time.sleep(5)
            self.alive = True
            print(f"[Nodo {self.node_id}] ¡RECUPERADO!")
            self.start_election()


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
