# server.py

import socket
import threading

PORT = 5050
clients = [] # list of connected players' sockets
player_slots = {}

def send_message(sock, message):
    sock.sendall((message + "\n").encode("utf-8")) #send message to one client: string -> bytes

def broadcast(message, source = None): #send msg to all clients 
    for client in clients[:]: #copy of clients list
        if client != source: # except one who sent the message
            try:
                send_message(client, message)
            except OSError:
                clients.remove(client)
                

def handle_client(client, address): # listens for messages from 1 client
    global player_slots
    try:
        if len(player_slots) == 0:
            role = "P1"
        elif len(player_slots) == 1:
            role = "P2"
        player_slots[client] = role
        send_message(client, f"ROLE:{role}")

        reader = client.makefile("r", encoding="utf-8") 
        for line in reader:
            msg = line.rstrip("\n")
            if not msg:
                break
            broadcast(msg, source=client)
    except (OSError, Exception):
        pass
    finally:
        if client in clients: # clear client list when disconnected
            clients.remove(client)
        if client in player_slots:
            del player_slots[client]
        client.close()

def accept_clients(server):
    while True:
        client, address = server.accept()
        clients.append(client)
        threading.Thread(target=handle_client, args=(client, address), daemon=True).start()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 5050))
    server.listen()
    print("Server running on port 5050")
    accept_clients(server)

if __name__ == "__main__":
    start_server()
