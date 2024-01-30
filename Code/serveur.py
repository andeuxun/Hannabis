# A non-blocking version of the multi-processed echo server
# Allows to terminate the program in a clean manner via Ctrl+C
 
import socket
import select
import signal
from multiprocessing import Process, Manager, Pipe
import time
import sysv_ipc
import random
import pickle
import json
 

serve = True
 
def handler(sig, frame):
    global serve
    if sig == signal.SIGINT:
 
        serve = False
 
 
def tirer_carte(game_dict):
    carte = random.choice(game_dict['pioche'])
    nouvelle_pioche = game_dict['pioche']
    nouvelle_pioche.remove(carte)
    game_dict['pioche'] = nouvelle_pioche
    return carte
 
def genererSetDepart(nombre_joueurs):
    pioche = []
    plateau=[]
    decks = {}
    infos_decks={}
    for i in range (1,nombre_joueurs+1):
        for j in range (1,6):
            if j == 1 : 
                for m in range (3):
                    pioche.append((j,i))
            elif j == 2 or j ==3 or j == 4 : 
                for m in range (2):
                    pioche.append((j,i))
            else:
                pioche.append((j,i))
    for j in range (1,nombre_joueurs+1):
        plateau.append([0,0,0,0,0])
        deck_joueur = []
        infos_deck_joueur = []
        for _ in range (5):
            carte = random.choice(pioche)
            deck_joueur.append(carte)
            infos_deck_joueur.append([[1,1,1,1,1],[1]*nombre_joueurs])
            pioche.remove((carte))
        infos_decks[str(j)]=infos_deck_joueur
        decks[str(j)] = deck_joueur
    return(pioche,decks,infos_decks,plateau)
 
 
 
 
def envoiInfosTour(socket, id_joueur,game_dict):
    paquet={"decks":{}, "plateau":game_dict['plateau'], "jetons":game_dict['jetons'], "turn":game_dict["turn"], "infos_decks":game_dict["infos_decks"]}
    for id_joueur_dico, main in game_dict["decks"].items():
        if int(id_joueur_dico)!=id_joueur:
            paquet["decks"][id_joueur_dico]=main
    envoi(socket, paquet)
 
def envoiInfosDepart(socket, id_joueur,game_dict):
    infos_depart={"id_joueur":id_joueur,"queue_key":game_dict["queue_key"],"nombre_joueurs":game_dict["nombre_joueurs"]}
    envoi(socket,infos_depart)
 
def changerTour(game_dict):
    if game_dict["turn"]==game_dict["nombre_joueurs"]:
        game_dict["turn"]=1
    else:
        game_dict["turn"]+=1
 
def receptionIndice(message,game_dict):
    infos_deck_temp=game_dict["infos_decks"]
    print("Reception d'un indice")
    print(message['classe'])
    print(message['indice'])
    if message['classe']=='chiffre':
        for carte in range(5):
 
            if game_dict['decks'][message['joueur']][carte][0]==message["indice"]:
 
                for i in range(5):
 
                    if i!=message["indice"]-1:
 
                        infos_deck_temp[message['joueur']][carte][0][i]=0
            else:
 
                infos_deck_temp[message['joueur']][carte][0][message["indice"]-1]=0       
    else:
        for carte in range(5):
            if game_dict['decks'][message['joueur']][carte][1]==(message["indice"]+1):
                for i in range(nombre_joueurs):
                    if i!=message["indice"]:
                        infos_deck_temp[message['joueur']][carte][1][i]=0
            else:
                infos_deck_temp[message['joueur']][carte][1][message["indice"]]=0
 
    game_dict["infos_decks"]=infos_deck_temp
 
def receptionCarte(message,game_dict):
    # Tester si la carte passe sur le plateau + piocher une nouvelle carte ( reset infos_carte )
    carte=game_dict['decks'][str(game_dict['turn'])][message['carte']-1]
    decks_temp=game_dict['decks']
 
    decks_temp[str(game_dict['turn'])][message['carte']-1]=tirer_carte(game_dict)
    game_dict['decks']=decks_temp
 
    infos_deck_temp=game_dict['infos_decks']
    infos_deck_temp[str(game_dict['turn'])][message['carte']-1]=[[1,1,1,1,1],[1]*nombre_joueurs]
    game_dict['infos_decks']=infos_deck_temp
 
    plateau_temp=game_dict['plateau']
    valide=True
 
    if carte[0]==1:
        if plateau_temp[carte[1]-1][0]==1:
            valide=False
    else:
        if plateau_temp[carte[1]-1][carte[0]-2]!=1:
            valide=False
 
    if valide:
        plateau_temp[carte[1]-1][carte[0]-1]=1
        game_dict['plateau']=plateau_temp
        return(1)
    return(0)
 
 
 
def client_handler(socket, address, id_joueur,game_dict):
    print(game_dict)
    with socket:
        print("Connected to client: ", address)
        envoiInfosDepart(socket, id_joueur,game_dict)
        time.sleep(1)
        while not game_dict['ready']:
            envoi(socket, "Pas assez de joueurs connectes")
            time.sleep(0.5)
        envoi(socket, "La partie peut commencer, voici le plateau de départ:")
        while True:
            envoiInfosTour(socket, id_joueur,game_dict)
 
            if game_dict["turn"]==id_joueur:
                print(f"Tour de {game_dict['turn']}")
                message=reception(socket)
                while message != "Fin du tour":
 
                    if message["type"]=="indice":
 
                        receptionIndice(message,game_dict)
 
                    if message["type"]=="carte":
 
                        resultat = receptionCarte(message,game_dict)
                        if resultat==1:
                            envoi(socket, "Succes")
                        else:
                            envoi(socket, "Echec")
 
                    message=reception(socket)
                changerTour(game_dict)
            else:
                tour_actuel=game_dict["turn"]
                while game_dict["turn"]==tour_actuel:
                    time.sleep(1)
 
 
 
 
 
 
 
 
def envoi(socket, paquet):
    socket.sendall(pickle.dumps(paquet))
 
def reception(socket):
    paquet=socket.recv(1024)
    return(pickle.loads(paquet))
 
 
if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
 
    nombre_joueurs= int(input("Nombre de clients à accepter: "))
    key = 128
 
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
 
    HOST = "localhost"
    PORT = 6666
    id_joueur=1
    joueurs_connectes = 0
 
    with Manager() as manager:
 
        game_dict = manager.dict()
        game_dict['nombre_joueurs']= nombre_joueurs
        game_dict['queue_key']=128
        game_dict['pioche'], game_dict['decks'] , game_dict["infos_decks"], game_dict["plateau"] = genererSetDepart(nombre_joueurs)
        game_dict['jetons']=[nombre_joueurs+3,3]
        game_dict['ready']=False
        game_dict['turn']=1
 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            server_socket.setblocking(False)
            server_socket.bind((HOST, PORT))
            server_socket.listen(nombre_joueurs)
            print(f"Le serveur écoute sur {HOST}:{PORT} et attend {nombre_joueurs} clients.")
 
            while serve :
                readable, writable, error = select.select([server_socket], [], [], 1)
                if server_socket in readable and joueurs_connectes < nombre_joueurs:
                    client_socket, address = server_socket.accept()
                    p = Process(target=client_handler, args=(client_socket, address, id_joueur,game_dict))
                    p.start()
                    joueurs_connectes+=1
                    id_joueur+=1
                if joueurs_connectes==nombre_joueurs:
                    game_dict['ready']=True
 
            server_socket.close()
            mq.remove()
 