import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QInputDialog, QLineEdit
from PyQt5.QtCore import Qt
from multiprocessing import Queue
import socket
import sysv_ipc
import time
import json
import pickle

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

class OutputWindow(QWidget):
    def __init__(self, queue, socket):
        super(OutputWindow, self).__init__()

        self.queue = queue
        self.socket = socket
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.text_edit = QTextEdit(self)
        layout.addWidget(self.text_edit)

        self.send_button = QPushButton('Send Message to Server', self)
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

        self.setWindowTitle('Output Window')
        self.setGeometry(100, 100, 600, 400)

        self.show()

    def closeEvent(self, event):
        sys.exit(0)

    def update_text(self, text):
        self.text_edit.append(text)

    def send_message(self, message):
        self.update_text(f"Sending message to server: {message}")
        self.socket.sendall(pickle.dumps({"type": "client_message", "content": message}))

    def get_user_input(self, prompt):
        text, ok = QInputDialog.getText(self, 'Input', prompt, QLineEdit.Normal)
        return text if ok else None

def verifEntree(possibilites, output_window):
    if possibilites and isinstance(possibilites[0], int):
        expected_type = int
    else:
        expected_type = str

    while True:
        entree = output_window.get_user_input(f"Ton choix parmi {possibilites}: ")

        if expected_type == int:
            try:
                entree = int(entree)
            except ValueError:
                output_window.update_text("Entrée invalide. Veuillez entrer un nombre.")
                continue

        if entree in possibilites:
            return entree
        else:
            output_window.update_text("Entrée invalide. Veuillez réessayer.")

def envoiIndice(joueur, classe, indice, output_window):
    paquet_indice = {"type": "indice", "joueur": str(joueur), "classe": classe, "indice": indice}
    for id_joueur in range(1, nombre_joueurs + 1):
        if id_joueur != num_joueur:
            envoi_mq(paquet_indice, id_joueur)
    envoi_socket(paquet_indice)
    output_window.update_text("Indice envoyé avec succès!")

def envoiCarte(carte, output_window):
    paquet_carte = {"type": "carte", "carte": carte}
    for id_joueur in range(1, nombre_joueurs + 1):
        if id_joueur != num_joueur:
            envoi_mq(paquet_carte, id_joueur)
    envoi_socket(paquet_carte)
    resultat = reception_socket(output_window)
    if resultat == "Succes":
        output_window.update_text("Reussi")
    else:
        output_window.update_text("Raté")

def jouerCarte(output_window):
    output_window.update_text("Quelle carte?")
    entree_carte = verifEntree([1, 2, 3, 4, 5], output_window)

    envoiCarte(entree_carte, output_window)
    time.sleep(2)

def donnerIndice(output_window):
    output_window.update_text("A quel joueur ?")
    entree_joueur = verifEntree([i for i in range(1, nombre_joueurs + 1) if i != num_joueur], output_window)
    output_window.update_text("Quel type d'indice ?")
    entree_classe = verifEntree(["couleur", "chiffre"], output_window)
    if entree_classe == "couleur":
        output_window.update_text("Quelle couleur ?")
        entree = verifEntree(couleurs, output_window)
        entree_indice = couleurs.index(entree)
    else:
        output_window.update_text("Quel chiffre ?")
        entree_indice = verifEntree([1, 2, 3, 4, 5], output_window)

    envoiIndice(entree_joueur, entree_classe, entree_indice, output_window)

    time.sleep(2)

def reception_socket(output_window):
    paquet = socket.recv(1024)
    data = pickle.loads(paquet)
    output_window.update_text(str(data))
    return data
 
def envoi_socket(paquet):
    socket.sendall(pickle.dumps(paquet))
 
def reception_mq():
    paquet=(mq.receive(type=num_joueur))[0]
    return(pickle.loads(paquet))
 
def envoi_mq(paquet, id):
    mq.send(pickle.dumps(paquet), type=id)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    output_queue = Queue()

    HOST = "localhost"
    PORT = 6666
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
        socket.connect((HOST, PORT))
        output_window = OutputWindow(output_queue, socket)
        infos_depart = reception_socket(output_window)
        num_joueur = infos_depart["id_joueur"]
        cle = infos_depart["queue_key"]
        nombre_joueurs = infos_depart["nombre_joueurs"]

        output_window.update_text(f"Vous etes le joueur n°{num_joueur}")

        mq = sysv_ipc.MessageQueue(cle)
        output_window.update_text(f"Connecté avec la clé : {cle}")

        output_window.update_text(f"Il y a {nombre_joueurs} joueurs")

        couleurs = couleurs[:nombre_joueurs]
        output_window.update_text(str(couleurs))

        message = reception_socket(output_window)
        while message == "Pas assez de joueurs connectes":
            output_window.update_text(message)
            message = reception_socket(output_window)
        output_window.update_text(message)

        while True:
            infos_tour = reception_socket(output_window)
            output_window.update_text(10 * "\n")
            output_window.update_text(str(infos_tour['plateau']))
            output_window.update_text(str(infos_tour['jetons']))
            output_window.update_text(f"Ta main :")
            for v in infos_tour['infos_decks'][str(num_joueur)]:
                output_window.update_text(str(v))
            for joueur, main in infos_tour["decks"].items():
                output_window.update_text(f"La main de {joueur} : {main}")

            if infos_tour["turn"] == num_joueur:
                output_window.update_text("C'est ton tour!")
                if infos_tour['jetons'][0] != 0:
                    output_window.update_text("Que veux tu faire ?\n1: Jouer une carte | 2: Donner un indice")
                    entree = verifEntree([1, 2],output_window)
                else:
                    output_window.update_text("Vous n'avez plus de jetons d'information, tentez de jouer une carte...")
                    entree = verifEntree([1, 2],output_window)

                if entree == 1:
                    jouerCarte(output_window)
                else:
                    donnerIndice(output_window)

                envoi_socket("Fin du tour")

            else:
                output_window.update_text(f"C'est le tour de {infos_tour['turn']}")
                paquet = reception_mq()
                if paquet["type"] == "indice":
                    article = "la" if paquet['classe'] == 'couleur' else "le"
                    indice = couleurs[paquet['indice']] if paquet['classe'] == 'couleur' else paquet['indice']
                    if int(paquet["joueur"]) == num_joueur:
                        output_window.update_text(f"{infos_tour['turn']} vous envoie un indice sur {article} {paquet['classe']} {indice} !")
                    else:
                        output_window.update_text(f"{infos_tour['turn']} envoie un indice à {paquet['joueur']} sur {article} {paquet['classe']} {indice} !")
                elif paquet["type"] == "carte":
                    output_window.update_text(f"{infos_tour['turn']} joue sa carte n°{paquet['carte']}")

    sys.exit(app.exec_())