# client
import socket
import sysv_ipc
import time
from multiprocessing import Process, Manager, Pipe
import json
import pickle
import os
from colored import bg, fg, attr
import shutil
from art import *

#colored module 
background = bg('108') + fg("black")
bold = attr("bold")
reset = attr("reset")
cards = bg("61") + fg("#0000FF")  # Blue text, black background
text = bg("#0000FF") + fg("white")  # Blue text, black background


color_dict = {
    "bleu": "#0000FF",
    "rouge": "#FF0000",
    "vert": "#00FF00",
    "jaune": "#FFFF00",
    "noir": "#000000",
    "blanc": "#FFFFFF",
    "orange": "#FFA500",
    "violet": "#800080",
    "rose": "#FFC0CB",
    "gris": "#808080",
    "marron": "#8B4513",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "lime": "#00FF00",
    "turquoise": "#40E0D0",
}

couleurs = [
    "bleu", 
    "rouge", 
    "vert", 
    "jaune", 
    "noir", 
    "blanc", 
    "orange", 
    "violet", 
    "rose", 
    "gris", 
    "marron", 
    "cyan", 
    "magenta", 
    "lime", 
    "turquoise"
]


def verifEntree(possibilites):
    if possibilites and isinstance(possibilites[0], int):
        expected_type = int
    else:
        expected_type = str
 
    while True:
        entree = input(f"Ton choix parmis {possibilites} : ")
 
        if expected_type == int:
            try:
                entree = int(entree)
            except ValueError:
                print("Entrée invalide. Veuillez entrer un nombre.")
                continue
 
        if entree in possibilites:
            return entree
        else:
            print("Entrée invalide. Veuillez réessayer.")
 
def envoiIndice(joueur, classe, indice):
    paquet_indice={"type":"indice", "joueur":str(joueur), "classe":classe,"indice":indice}
    for id_joueur in range (1, nombre_joueurs+1):
        if id_joueur!=num_joueur:
            envoi_mq(paquet_indice, id_joueur)
    envoi_socket(paquet_indice)
 
def envoiCarte(carte):
    paquet_carte={"type":"carte","carte":carte}
    for id_joueur in range (1, nombre_joueurs+1):
        if id_joueur!=num_joueur:
            envoi_mq(paquet_carte, id_joueur)
    envoi_socket(paquet_carte)
    resultat=reception_socket()
    if resultat=="Succes":
        print("Reussi")
    else:
        print("Raté")
 
def jouerCarte():
    print("Quelle carte?")
    entree_carte=verifEntree([1,2,3,4,5])
 
    envoiCarte(entree_carte)
    time.sleep(2)
 
def donnerIndice():
    print("A quel joueur ?")
    entree_joueur = verifEntree([i for i in range(1, nombre_joueurs + 1) if i != num_joueur])
    print("Quel type d'indice ?")
    entree_classe = verifEntree(["couleur","chiffre"])
    if entree_classe=="couleur":
        print("Quelle couleur ?")
        entree=verifEntree(couleurs)
        entree_indice=couleurs.index(entree)
    else:
        print("Quel chiffre ?")
        entree_indice=verifEntree([1,2,3,4,5])
 
    envoiIndice(entree_joueur,entree_classe,entree_indice)
 
    time.sleep(2)
 
def reception_socket():
    paquet=socket.recv(1024)
    return(pickle.loads(paquet))
 
def envoi_socket(paquet):
    socket.sendall(pickle.dumps(paquet))
 
def reception_mq():
    paquet=(mq.receive(type=num_joueur))[0]
    return(pickle.loads(paquet))
 
def envoi_mq(paquet, id):
    mq.send(pickle.dumps(paquet), type=id)

def printJeton(jetons):
    v,k = str(jetons[0]),str(jetons[1])
    print("Il vous reste : " + v + " Information token and " + k + " Fuze token\n")

def printWelcome(num_joueur,clef,nombre_joueurs,couleurs):
    os.system(f'echo "\\033]0;Hannabis : Player {num_joueur}\\007"')
    tprint("test","rnd-xlarge")
    print(f"{background}{bold}Welcome to Hanabi! Work together to create a stunning fireworks display. Give and receive clues to play cards in the right order. Good luck!", end = "")
    print()
    print(f"Vous etes le joueur n°{num_joueur}")
    print(f"Connecté avec la clé : {cle}")
    print(f"Il y a {nombre_joueurs} joueurs")
    print(couleurs)

def printMains(mains):
    print(f"\n{background}")
    column,_= shutil.get_terminal_size()
    padding = (column - 5 * (len("███████") + len("    "))) // 2
    for i in range(5):
        print(f" "*padding, end="")
        for j in range(len(mains)):
            num,color = mains[j]
            if color < 1 :
                c = fg(color_dict['gris']) + bg(color_dict['gris'])
                print(f"{c}███████", end="")
            else : 
                c = fg(color_dict[couleurs[color - 1]]) + bg(color_dict[couleurs[color - 1]])
                if i != 2:
                    print(f"{c}███████", end="")
                else:
                    print(f"{c}███{fg('black') + bg(color_dict[couleurs[color - 1]])}{num}{c}███", end="")
            print(f"{background}    ", end="")
        print()
    print(f" "*padding, end="")
    for j in range(len(mains)):
        print(f"{background}   {j + 1}       ", end="")

    print(f"\n{background}")


 
if __name__ == '__main__':
    HOST = "localhost"
    PORT = 6666
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:  
        socket.connect((HOST, PORT))
 
        infos_depart=reception_socket()
        num_joueur=infos_depart["id_joueur"]
        cle=infos_depart["queue_key"]
        nombre_joueurs=infos_depart["nombre_joueurs"]
 
        mq = sysv_ipc.MessageQueue(cle) 
        couleurs=couleurs[:nombre_joueurs]

        printWelcome(num_joueur,cle,nombre_joueurs,couleurs)
 
        message=reception_socket()
        while message == "Pas assez de joueurs connectes":
            
            for char in "|/-\\":
                print(f"\rWaiting for players to connect {char} ", end="")
                time.sleep(0.1)
            message=reception_socket()
        print(message)
 
 
        # Début du premier tour
        while True:
            infos_tour=reception_socket()
            print("\n")
            print(infos_tour['plateau'])

            ## Print jetons :
            print(infos_tour['jetons'])
            printJeton(infos_tour['jetons'])
            print(f"Ta main :")
            player_hand = []
            for carte in infos_tour['infos_decks'][str(num_joueur)]:
                num = carte[0].index(1)
                color = carte[1].index(1)
                if num == 0 and carte[0][1] == 1 :
                    num = -1
                if color == 0 and carte[1][1] == 1 :
                    color = -1
                player_hand.append((num,color))
            
            printMains(player_hand)

            for joueur,mains in infos_tour["decks"].items():
                print(f"La main de {joueur} : \n")
                printMains(mains)

            #afficherJeu(infos_tour,main_perso)
            if infos_tour["turn"]==num_joueur:
                print("C'est ton tour!")
                if infos_tour['jetons'][0]!=0:
                    print("Que veux tu faire ?\n1: Jouer une carte | 2: Donner un indice")
                    entree=verifEntree([1,2])
                else:
                    print("Vous n'avez plus de jetons d'information, tentez de jouer une carte...")
                    entree=verifEntree([1,2])
 
                if entree==1:
                    jouerCarte()
                else:
                    donnerIndice()
 
                envoi_socket("Fin du tour")
 
            else:
                print(f"C'est le tour de {infos_tour['turn']}")
                paquet=reception_mq()
                if paquet["type"]=="indice":
                    article = "la" if paquet['classe'] == 'couleur' else "le"
                    indice = couleurs[paquet['indice']] if paquet['classe'] == 'couleur' else paquet['indice']
                    if int(paquet["joueur"])==num_joueur:
                        print(f"{infos_tour['turn']} vous envoie un indice sur {article} {paquet['classe']} {indice} !")
                    else:
                        print(f"{infos_tour['turn']} envoie un indice à {paquet['joueur']} sur {article} {paquet['classe']} {indice} !")
                elif paquet["type"]=="carte":
                    print(f"{infos_tour['turn']} joue sa carte n°{paquet['carte']}")