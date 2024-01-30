import socket
import select
import signal
from multiprocessing import Process, Manager, Pipe
import time
import sysv_ipc
import random
import pickle
import json
 
 
global serve
serve = True
 
def handler(sig, frame):
    """
    This function handles signals. 
    When SIGINT is received, it makes sure all processes are 
    properly closed and killed before quiting. 
    """
    try:
        if sig == signal.SIGINT : #or not game_dict['gamePlaying']
            close_all()
    except Exception as e:
        print(f"There was a problem with the handler. Running processes could not be killed. Error: ",e)
 
def close_all():
    global serve
    try:
        mq.remove()
        serve = False
        print("Closed mq properly.\n")
    except Exception as e:
        print("Could not close queue: ", e)
 
    try:
        serve = False
        for p in running_processes:
            p.kill()
        print("Killed processes properly.\n")
    except Exception as e:
        print("Could not kill processes: ", e)
 
def pick_card(game_dict):
    """
    Picks a random card in the deck and sets the new deck.
    Tests if deck is empty before. 
    No params.
    Returns the card that was picked.
    """
    global serve
    if len(game_dict['deck']) != 0:
        card = random.choice(game_dict['deck'])
        nouvelle_pioche = game_dict['deck']
        nouvelle_pioche.remove(card)
        game_dict['deck'] = nouvelle_pioche
        return card
    else:
        game_dict['gamePlaying'] = False
        serve = False
        for socket in game_dict['sockets']: 
            envoi(socket,{"EOG":True,"Reason_EOG":"Deck is empty."})    
        return "EOG"
 
 
def hideHands(numberOfPlayers):
    """
    Generates the hands that will be shown to the players by 
    displaying an array of 1's for colors and numbers that 
    will later be modified to show a player the clues he was given.
    NumberOfPlayers as param.
    """
    hands_infos={}
    for j in range (1,numberOfPlayers+1):
        player_hand_info = []
        for k in range (5):
            player_hand_info.append([[1,1,1,1,1],[1]*numberOfPlayers])
        hands_infos[str(j)]=player_hand_info
    return hands_infos
 
 
def deckStartup(numberOfPlayers, game_dict):
    """
    Generates the deck that will be used throughout the game.
    Since in this hannabis version the number of types of cards 
    depends on the numberof players, takes numberOfPlayers as argument.
    """
    try:
        deck = []
        color_deck = [1,1,1,2,2,3,3,4,4,5]
        for i in range (1,numberOfPlayers+1):
            for j in color_deck:
                deck.append((j,i))
        print(f"Deck that will be used is:{deck}")
        game_dict['deck'] = deck
        return 0
 
    except Exception as e:
        print(f"There was a problem in deckStartup(): ",e)
        return -1
 
 
def handsStartup(numberOfPlayers, game_dict):
    """
    Picks random cards in the deck and assigns them to the different
    players so that each player has a hand (5 cards each).
    Again, takes numberOfPlayers as argument to build the correct
    number of hands.
    """
    try:
        hands = {}
        for j in range (1,numberOfPlayers+1):
            player_hand = []
            for k in range (5):
                card = pick_card(game_dict)
                player_hand.append(card)
            hands[str(j)] = player_hand
        game_dict['hands'] = hands
        return 0
    except Exception as e:
        print(f"There was a problem with handsStartup: ",e)
        return -1
 
def gameBoardSetup(numberOfPlayers, game_dict):
    """
    Generates the gameboard that will be used, with the right number
    of colors.
    Takes numberOfPlayers as param.
    """
    try:
        tmp_game_board = []
        for i in range(numberOfPlayers):
            tmp_game_board.append([0,0,0,0,0])
        game_dict['game_board'] = tmp_game_board    
        return 0
    except Exception as e:
        print(f"There was a problem with gameBoardSetup(): ", e)
        return -1
 
def sendTurnUpdate(socket, player_num, game_dict):
    """
    Handles the sending of the updates to each player through the sockets.
    This function is called everytime a turn starts, so players have the 
    same and updated info to play.
 
    Args:
        (socket and number) assigned to the player that needs to be 
        sent the information
    Returns:
        None
    """
    paquet={
        "hands":{}, 
        "game_board":game_dict['game_board'], 
        "tokens":game_dict['tokens'], 
        "turn":game_dict["turn"], 
        "infos_decks":game_dict["infos_decks"]
        }
 
    for player_num_dico, main in game_dict["hands"].items():
        if int(player_num_dico)!=player_num:
            paquet["hands"][player_num_dico]=main
    envoi(socket, paquet)
 
def sendFirstTurn(socket, player_num, game_dict):
    """
    Same role as sendTurnUpdate, but this one is specifically and
    only called for the first turn (sending infos that only need
    to be sent during initialisation).
 
    Args:
        (socket and number) assigned to the player that needs to be 
        sent the information
    Returns: 
        None
    """
    infos_depart={
        "player_num":player_num,
        "queue_key":game_dict["queue_key"],
        "numberOfPlayers":game_dict["numberOfPlayers"]
        }
    envoi(socket,infos_depart)
 
def change_turns(game_dict):
    """
    Handles change of turn: next player or back to first
    player if last player was playing.
 
    Args:
        None
    Returns:
        None
    """
    if game_dict["turn"]==game_dict["numberOfPlayers"]:
        game_dict["turn"]=1
    else:
        game_dict["turn"]+=1
 
 
def clueHandle(message, game_dict):
    """
    Processes and updates game information based on the clue received from a player.
    Interprets the received clue (color or number) and modifies 'infos_deck' inside 
    game_dict to reflect the clue to the concerned player.
 
    Args:
        message (dict): dictionnary sent by the players containing the clue and 
        game information
    Returns:
        None
    """
    infos_deck_tmp=game_dict["infos_decks"]
    print("Received clue:")
    print(message['classe'])
    print(message['indice'], "\n")
    if message['classe']=='chiffre':
        count = 0
        for card in game_dict['hands'][message['joueur']]:
            print(card[0])
 
            if card[0]==message['indice']:
 
                for i in range(5):
                    if i != (message['indice']-1):
                        infos_deck_tmp[message['joueur']][count][0][i]=0
                    else:
                        infos_deck_tmp[message['joueur']][count][0][i]=message['indice']
            count += 1
 
    else:
        for card in range(5):
            if game_dict['hands'][message['joueur']][card][1]==(message["indice"]+1):
                for i in range(numberOfPlayers):
                    if i!=message["indice"]:
                        infos_deck_tmp[message['joueur']][card][1][i]=0
            else:
                # print(infos_deck_tmp,"\n")
                # print(infos_deck_tmp[message['joueur']][card][1])
                infos_deck_tmp[message['joueur']][card][0][message["indice"]-1]=0
    token_tmp = game_dict['tokens']
    token_tmp[0] -= 1
    game_dict['tokens'] = token_tmp
    print(f"Tokens for clues: ",game_dict['tokens'])
    game_dict["infos_decks"]=infos_deck_tmp
 
def receptioncard(message, game_dict):
    """
    Processes card played by a player, picks a new card for them and checks if the 
    card played fits on the board. Places it on the board if it does, discards 
    it if not. 
    Modifies 'hands', 'infos_decks', and 'game_board' of game_dict dictionnary.
 
    Args:
        message (dict): dictionnary sent by the players containing the clue and 
        game information
    Returns:
        int: 1 if the card fits on the game board, 0 otherwise.
    """
    while game_dict['gamePlaying']:
        card=game_dict['hands'][str(game_dict['turn'])][message['card']-1]
        hands_tmp=game_dict['hands']
 
        hands_tmp[str(game_dict['turn'])][message['card']-1]= pick_card(game_dict)
        game_dict['hands']=hands_tmp
 
 
        infos_deck_tmp=game_dict['infos_decks']
        infos_deck_tmp[str(game_dict['turn'])][message['card']-1]=[[1,1,1,1,1],[1]*numberOfPlayers]
        game_dict['infos_decks']=infos_deck_tmp
 
        plateau_tmp=game_dict['game_board']
        valide=True
        print(f"Going to check if card fits")
 
        if card[0]==1:
            if plateau_tmp[card[1]-1][0]==1:
                valide=False
        else:
            if plateau_tmp[card[1]-1][card[0]-2]!=1:
                valide=False
 
        if valide:
            plateau_tmp[card[1]-1][card[0]-1]=1
            game_dict['game_board']=plateau_tmp
            return(1)
        return(0)
 
 
 
def client_handler(socket, address, player_num, game_dict):
    """
    Handles communication with a connected player during the game.
 
    Args:
        socket (socket.socket): The socket object representing the communication channel with the player.
        address (tuple): The address of the connected player.
        player_num (int): The player's number.
 
    The function establishes communication with the connected player, exchanges initial game information, and manages the player's turn. It continuously sends and receives game information until the game concludes. During the player's turn, the function waits for the player's actions, such as providing clues or playing cards, and responds accordingly. The function also handles the end-of-game scenario, updating the player with the reason for the game's conclusion.
 
    The function returns 0 when the player's connection is closed or when the game ends.
 
    Returns:
        int: 0 when the player's connection is closed or when the game ends.
    """
    global serve
    with socket:
        print("Connected to client: ", address)
        sendFirstTurn(socket, player_num, game_dict)
        time.sleep(1)
        while not game_dict['ready']:
            envoi(socket, "Waiting for players...")
            time.sleep(1)
        envoi(socket, "Game can start, here is the gameboard")
        time.sleep(1) # Wait for Loading Screen
        while game_dict['gamePlaying']:
            sendTurnUpdate(socket, player_num, game_dict)
 
            if game_dict["turn"]==player_num:
                print(f"{game_dict['turn']}'s turn")
                message=reception(socket)
                while message != "End of Turn":
 
                    if message["type"]=="indice":
 
                        clueHandle(message, game_dict)
 
                    if message["type"]=="card":
 
                        resultat = receptioncard(message, game_dict)
                        if not game_dict['gamePlaying']:
                            envoi(socket,{"EOG":True,"Reason_EOG":"Deck is empty."})
                            return -1
                        if resultat:
                            envoi(socket, "Success")
                            print("Card fits on board !\n")
                        else:
                            envoi(socket, "Failed")
                            print("Card doesn't fit on board ...\n")
                            token_tmp = game_dict['tokens']
                            token_tmp[1] -= 1
                            game_dict['tokens'] = token_tmp
                        if game_dict['tokens'][1] == 0:
                            print("Closing game bcs no more tokesn")
                            game_dict['gamePlaying'] = False
                            envoi(socket,{"EOG":True,"Reason_EOG":"No more play tokens."})
                            return -1
 
                    message=reception(socket)
                change_turns(game_dict)
            else:
                tour_actuel=game_dict["turn"]
                while game_dict["turn"]==tour_actuel:
                    time.sleep(1)
        return 0
 
 
def envoi(socket, paquet):
    socket.sendall(pickle.dumps(paquet))
 
def reception(socket):
    paquet=socket.recv(1024)
    return(pickle.loads(paquet))
 
 
if __name__ == '__main__':
    running_processes = []
    client_sockets = []
    signal.signal(signal.SIGINT, handler)
 
    numberOfPlayers = int(input("How many players will be joining ? "))
    key = 128
 
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
 
    HOST = "localhost"
    PORT = 6666
    player_num =1
    joueurs_connectes = 0
 
    with Manager() as manager:
        
        game_dict = manager.dict()
        game_dict['gamePlaying'] = True
        game_dict['numberOfPlayers']= numberOfPlayers
        game_dict['queue_key']=128
        deckStartup(numberOfPlayers, game_dict)
        handsStartup(numberOfPlayers, game_dict) 
        game_dict["infos_decks"] = hideHands(numberOfPlayers)
        gameBoardSetup(numberOfPlayers, game_dict)
        game_dict['tokens']=[numberOfPlayers+3,3]
        game_dict['ready']=False
        game_dict['turn']=1
        game_dict['sockets'] = []
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            
            server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            server_socket.setblocking(False)
            server_socket.bind((HOST, PORT))
            server_socket.listen(numberOfPlayers)
            print(f"Game server started on {HOST}:{PORT} and expecting {numberOfPlayers} players.")
 
            while serve :
                readable, writable, error = select.select([server_socket], [], [], 1)
                if server_socket in readable and joueurs_connectes < numberOfPlayers:
                    client_socket, address = server_socket.accept()
                    client_sockets.append(client_socket)
                    game_dict['sockets'] = client_sockets
                    p = Process(target=client_handler, args=(client_socket, address, player_num, game_dict))
                    p.start()
                    running_processes.append(p)
 
                    joueurs_connectes+=1
                    player_num +=1
                if joueurs_connectes==numberOfPlayers:
                    game_dict['ready']=True
                if not game_dict['gamePlaying']:
                    serve = False
                    print(f"Closing sockets and killing processes for EOG...\n")
                    close_all()
                    try:
                        for client_socket in game_dict['sockets']: client_socket.close()
                    except Exception as e:
                        print(f"Sockets already closed.")    
            for client_socket in game_dict['sockets']: client_socket.close()
            server_socket.detach()
            server_socket.close()
            print('Closed connections properly\n')