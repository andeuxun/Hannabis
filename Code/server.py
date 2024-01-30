# server
import random
import pickle
import socket
import select
import signal
from multiprocessing import Process, Manager, Pipe
import time
import sysv_ipc

 
 
global serve
serve = True

 
def handler(sig, frame):
    """
    This function handles signals. 
    When SIGINT is received, it makes sure all processes are 
    properly closed and killed before quiting. 
    """
    try:
        if sig == signal.SIGINT or not main_dict['gamePlaying']:
            close_all()
    except Exception as e:
        print(f"There was a problem with the handler. Running processes could not be killed. Error: ",e)

def close_all():
    """
    This function ensures that the message queue as well as all child
    processes are closed properly. It is only called when the game 
    finishes.

    Args:
        None
    Returns:
        None
    """
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

def pick_card():
    """
    Picks a random card in the deck and sets the new deck.
    Tests if deck is empty before. 
    
    Args:
        None
    Returns:
        (tuple) card, the card that was picked if deck is not empty.
        (string) EOG=End Of Game if deck is empty.
    """
    global serve
    if len(main_dict['deck']) != 0:
        card = random.choice(main_dict['deck'])
        nouvelle_pioche = main_dict['deck']
        nouvelle_pioche.remove(card)
        main_dict['deck'] = nouvelle_pioche
        return card
    else:
        if main_dict['game_board'][0][4] == 1 or main_dict['game_board'][1][4] == 1 :
            return (0,0)
        else:    
            main_dict['gamePlaying'] = False
            serve = False
            for socket in main_dict['sockets']: 
                socketSend(socket,{"EOG":True,"Reason_EOG":"Deck is empty."})    
            return "EOG"
    
 
def hideHands(numberOfPlayers):
    """
    Generates the hands that will be shown to the players by 
    displaying an array of 1's for colors and numbers that 
    will later be interpreted to show a player the clues he was given.

    Args:
        numberOfPlayers (int) : number of players in the game.
    Returns:
        (dict) hands_infos, a dictionnary containing the "hidden" hands 
        for each player
    """
    hands_infos={}
    for j in range (1,numberOfPlayers+1):
        player_hand_info = []
        for k in range (5):
            player_hand_info.append([[1,1,1,1,1],[1]*numberOfPlayers])
        hands_infos[str(j)]=player_hand_info
    return hands_infos
 

def deckStartup(numberOfPlayers):
    """
    Generates the deck that will be used throughout the game.
    Since in this hannabis version the number of types of cards 
    depends on the numberof players.
    
    Args:
        numberOfPlayers (int) : number of players in the game.
    Returns:
        (int) 0 if deck is generated with no issue
        (int) -1 if an Exception was raised
    """
    try:
        deck = []
        color_deck = [1,1,1,2,2,3,3,4,4,5]
        for i in range (1,numberOfPlayers+1):
            for j in color_deck:
                deck.append((j,i))
        print(f"Deck that will be used is:{deck}")
        main_dict['deck'] = deck
        return 0
     
    except Exception as e:
        print(f"There was a problem in deckStartup(): ",e)
        return -1


def handsStartup(numberOfPlayers):
    """
    Picks random cards in the deck and assigns them to the different
    players so that each player has a hand (5 cards each).

    Args:
        numberOfPlayers (int) : number of players in the game.
    Returns:
        (int) 0 if hands are generated with no issue
        (int) -1 if an Exception was raised
    """
    try:
        hands = {}
        for j in range (1,numberOfPlayers+1):
            player_hand = []
            for k in range (5):
                card = pick_card()
                player_hand.append(card)
            hands[str(j)] = player_hand
        main_dict['hands'] = hands
        return 0
    except Exception as e:
        print(f"There was a problem with handsStartup: ",e)
        return -1

def gameBoardSetup(numberOfPlayers):
    """
    Generates the gameboard that will be used, with the right number
    of colors.

    Args:
        numberOfPlayers (int) : number of players in the game.
    Returns:
        (int) 0 if game board is generated with no issue
        (int) -1 if an Exception was raised
    """
    try:
        tmp_game_board = []
        for i in range(numberOfPlayers):
            tmp_game_board.append([0,0,0,0,0])
        main_dict['game_board'] = tmp_game_board    
        return 0
    except Exception as e:
        print(f"There was a problem with gameBoardSetup(): ", e)
        return -1

def sendTurnUpdate(socket, player_num):
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
        "game_board":main_dict['game_board'], 
        "tokens":main_dict['tokens'], 
        "turn":main_dict["turn"], 
        "infos_decks":main_dict["infos_decks"]
        }
    
    for player_num_dico, main in main_dict["hands"].items():
        if int(player_num_dico)!=player_num:
            paquet["hands"][player_num_dico]=main
    socketSend(socket, paquet)
 
def sendFirstTurn(socket, player_num):
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
        "queue_key":main_dict["queue_key"],
        "numberOfPlayers":main_dict["numberOfPlayers"]
        }
    socketSend(socket,infos_depart)
 
def changeTurns():
    """
    Handles change of turn: next player or back to first
    player if last player was playing.

    Args:
        None
    Returns:
        None
    """
    if main_dict["turn"]==main_dict["numberOfPlayers"]:
        main_dict["turn"]=1
    else:
        main_dict["turn"]+=1


def clueHandle(message):
    """
    Processes and updates game information based on the clue received from a player.
    Interprets the received clue (color or number) and modifies 'infos_deck' inside 
    main_dict to reflect the clue to the concerned player.

    Args:
        message (dict): dictionnary sent by the players containing the clue and 
        game information
    Returns:
        None
    """
    infos_deck_tmp=main_dict["infos_decks"]
    print("Received clue:")
    print(message['classe'])
    print(message['indice'], "\n")
    if message['classe']=='number':
        count = 0
        for card in main_dict['hands'][message['joueur']]:
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
            if main_dict['hands'][message['joueur']][card][1]==(message["indice"]+1):
                for i in range(numberOfPlayers):
                    if i!=message["indice"]:
                        infos_deck_tmp[message['joueur']][card][1][i]=0
            else:
                # print(infos_deck_tmp,"\n")
                # print(infos_deck_tmp[message['joueur']][card][1])
                infos_deck_tmp[message['joueur']][card][0][message["indice"]-1]=0
    token_tmp = main_dict['tokens']
    token_tmp[0] -= 1
    main_dict['tokens'] = token_tmp
    print(f"Tokens for clues: ",main_dict['tokens'])
    main_dict["infos_decks"]=infos_deck_tmp
 
def receptioncard(message):
    """
    Processes card played by a player, picks a new card for them and checks if the 
    card played fits on the board. Places it on the board if it does, discards 
    it if not. 
    Modifies 'hands', 'infos_decks', and 'game_board' of main_dict dictionnary.

    Args:
        message (dict): dictionnary sent by the players containing the clue and 
        game information
    Returns:
        (int) 1 if the card fits on the game board, 0 otherwise.
    """
    while main_dict['gamePlaying']:
        card=main_dict['hands'][str(main_dict['turn'])][message['card']-1]
        hands_tmp=main_dict['hands']
        
        hands_tmp[str(main_dict['turn'])][message['card']-1]= pick_card()
        main_dict['hands']=hands_tmp


        infos_deck_tmp=main_dict['infos_decks']
        infos_deck_tmp[str(main_dict['turn'])][message['card']-1]=[[1,1,1,1,1],[1]*numberOfPlayers]
        main_dict['infos_decks']=infos_deck_tmp

        plateau_tmp=main_dict['game_board']
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
            main_dict['game_board']=plateau_tmp
            return(1)
        return(0)
 
 
 
def playerHandler(socket, address, player_num):
    """
    Handles communication with a connected player during the game.
    This function is the target of the child processes that are started each time a new
    player connects. They manage the players turn, all of the communication with the 
    player (sending and receiving game updates). This function also signals the end of 
    the game to its assigned player. 

    Args:
        socket (socket.socket): The socket object assigned to the player.
        address (tuple): The address of the connected player.
        player_num (int): The player's number.
    Returns:
        (int) 0 when the player's connection is closed or when the game ends.
    """
    global serve
    with socket:
        print("Connected to client: ", address)
        sendFirstTurn(socket, player_num)
        time.sleep(1)
        while not main_dict['ready']:
            socketSend(socket, "Waiting for players...")
            time.sleep(1)
        socketSend(socket, "Game can start, here is the gameboard")
        time.sleep(1) # Wait for Loading Screen
        while main_dict['gamePlaying']:
            sendTurnUpdate(socket, player_num)

            if main_dict["turn"]==player_num:
                print(f"{main_dict['turn']}'s turn")
                message=socketReceive(socket)
                while message != "End of Turn":
 
                    if message["type"]=="indice":
 
                        clueHandle(message)
 
                    if message["type"]=="card":
 
                        resultat = receptioncard(message)
                        if not main_dict['gamePlaying']:
                            socketSend(socket,{"EOG":True,"Reason_EOG":"Deck is empty."})
                            return -1
                        if resultat:
                            socketSend(socket, "Success")
                            print("Card fits on board !\n")
                        else:
                            socketSend(socket, "Failed")
                            print("Card doesn't fit on board ...\n")
                            token_tmp = main_dict['tokens']
                            token_tmp[1] -= 1
                            main_dict['tokens'] = token_tmp
                        if main_dict['tokens'][1] == 0:
                            print("Closing game bcs no more tokesn")
                            main_dict['gamePlaying'] = False
                            socketSend(socket,{"EOG":True,"Reason_EOG":"No more play tokens."})
                            return -1

                    message=socketReceive(socket)
                changeTurns()
            else:
                tour_actuel=main_dict["turn"]
                while main_dict["turn"]==tour_actuel:
                    time.sleep(1)
        return 0
 
 
def socketSend(socket, paquet):
    """
    This function sends a message to a socket using pickle.
    Args:
        socket (socket.socket) : socket object representing the connection with a player.
        paquet (str/int/dict/list) : data to be sent to the player.
    Returns:
        None
    """
    socket.sendall(pickle.dumps(paquet))
 
def socketReceive(socket):
    """
    This function receives a message through the socket.
    Args:
        socket (socket.socket) : socket object representing the connection with a player.
    Returns:
        Returns the received message.
    """
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
    player_num = 1
    joueurs_connectes = 0
 
    with Manager() as manager:
 
        main_dict = manager.dict()
        main_dict['gamePlaying'] = True
        main_dict['numberOfPlayers']= numberOfPlayers
        main_dict['queue_key']=128
        deckStartup(numberOfPlayers)
        handsStartup(numberOfPlayers) 
        main_dict["infos_decks"] = hideHands(numberOfPlayers)
        gameBoardSetup(numberOfPlayers)
        main_dict['tokens']=[numberOfPlayers+3,3]
        main_dict['ready']=False
        main_dict['turn']=1
        main_dict['sockets'] = []
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
                    main_dict['sockets'] = client_sockets
                    p = Process(target=playerHandler, args=(client_socket, address, player_num))
                    p.start()
                    running_processes.append(p)

                    joueurs_connectes+=1
                    player_num +=1
                if joueurs_connectes==numberOfPlayers:
                    main_dict['ready']=True
                if (not main_dict['gamePlaying']) or (main_dict['game_board'][0][4] == 1 and main_dict['game_board'][1][4] == 1):
                    serve = False
                    print(f"Closing sockets and killing processes for EOG...\n")
                    close_all()
                    try:
                        for client_socket in main_dict['sockets']: 
                            if main_dict['game_board'][0][4]==1: socketSend(client_socket,{"EOG":True,"Reason_EOG":"You won !"})
                            client_socket.close()
                    except Exception as e:
                        print(f"Sockets already closed.") 

            for client_socket in main_dict['sockets']: client_socket.close()
            server_socket.detach()
            server_socket.close()
            print('Closed connections properly\n')