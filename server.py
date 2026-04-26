import threading
from socket import *

HOST = "0.0.0.0"
PORT = 1111

clients = []


def broadcast(message, sender=None):
    """Отправка всем клиентам"""
    for c in clients:
        try:
            c.send(message)
        except:
            if c in clients:
                clients.remove(c)


def handle_client(conn):
    buffer = ""

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                # пересылаем ВСЕМ
                broadcast((line + "\n").encode(), conn)

        except:
            break

    if conn in clients:
        clients.remove(conn)

    conn.close()


server = socket(AF_INET, SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Server started on port", PORT)

while True:
    conn, addr = server.accept()
    print("Client connected:", addr)

    clients.append(conn)

    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()