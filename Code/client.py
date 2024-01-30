# client
import socket
import sysv_ipc
import time
from multiprocessing import Process, Manager, Pipe
import json
import pickle
import sys
import os
from colored import bg, fg, attr
from art import *
 
global playing

color_dict = {
    "blue": 21,
    "red": 124,
    "green": 106,
    "orange": 215,
    "yellow": 184,
    "purple": 54,
    "black": 0,
    "white": 15,
    "gray": 242,
}

colors = [
    "blue", 
    "red", 
    "green", 
    "yellow", 
    "orange", 
    "purple"
]

VOID_STYLE = bg('steel_blue')
TEXT_WHITE = fg("white") + attr("bold")
TEXT_BLACK = fg("black")

print(f"{VOID_STYLE}")


def cardInput():
    """
    Asks the user to choose a card. Also so does input checking to make sure a number
    between 1 and 5 is input by the user.
    Args:
        None 
    Returns:
        (int) the number chosen by the user corresponding to a card.
    """
    while True:
        entree = input(f"\nSelect a number from 1 to 5 : ")
        try:
            if 1 <= int(entree) <= 5:
                return int(entree)
        except:
            print("Invalid input.\n")
            continue
    
def playerInput():
    """
    Asks the user to choose a player to send a clue to. Also so does input checking 
    to make sure user input is valid.
    Args:
        None 
    Returns:
        (int) the number chosen by the user corresponding to a player.
    """
    while True:
        entree = input(f"\nWhich player do you want to send the clue to ?\n\nEnter a number between 1 and {numberOfPlayers} : ")
        try:
            if 1 <= int(entree) <= numberOfPlayers and int(entree) != player_num:
                return int(entree)
        except:
            print("Invalid input.\n")
            continue
        
def clueInput():
    """
    Asks the user to choose a type of clue. Also so does input checking to 
    make sure user input is valid.
    Args:
        None 
    Returns:
        (string) the type of clue chosen by the user.
    """
    while True:
        entree = input(f"\nDo you want to give a color clue or a number clue ?\n\nPlease type 'color' or 'number' : ")
        try:
            if entree == 'color' or entree == 'number':
                return entree
        except:
            print("Invalid input.\n")

def colorInput(colors):
    """
    Asks the user to choose a color. Also so does input checking to 
    make sure user input is valid. Displays the list of available colors
    in the game.
    Args:
        None 
    Returns:
        (string) the color chosen by the user.
    """
    colors_list = ""
    for i in range (len(colors)):
        colors_list += f"{i+1}. {colors[i]}\n"
    while True:
        entree = input(f"What color do you want to clue ?\n\nPlease choose your color from the following list :\n   {colors} \n\nType the corresponding number :")
        try:
            if entree in colors:
                return entree
        except:
            print("Invalid input.\n")

def moveInput():
    """
    Asks the user to choose move(play/give a clue). Also so does input checking to 
    make sure user input is valid.
    Args:
        None 
    Returns:
        (int) number chosen by user corresponding to a move.
    """
    while True:
        entree = input(f"Choose a move:\n     1.Play a card\n     2.Give a clue\n")
        try:
            if int(entree) == 1 or int(entree) == 2:
                return int(entree)
        except:
            print("Invalid input. Please enter a number between 1 and 2.")
 
def sendClue(joueur, classe, indice):
    """
    Send a specific clue to a player through the message queue.
    Tells the other player a clue was sent.
    Args:
        joueur (int) : number of the player to send the clue to.
        classe (string) : type of the clue (color/number)
        indice (string) : color or number to be clued.
    Returns:
        None
    """
    paquet_indice={"type":"indice", "joueur":str(joueur), "classe":classe,"indice":indice}
    for player in range (1, numberOfPlayers+1):
        print(f"{player_num}, {numberOfPlayers}")
        if player!=player_num:
            mqSend(paquet_indice, player)
            print(f"Sent{paquet_indice} to player {player}")
            time.sleep(2)
    socketSend(paquet_indice)
 
def sendCard(card):
    """
    Sends a card to be played through the socket and waits for response from the game
    process to know wether card fits on the board or not. Also tells the other players
    a card was played.
    Args:
        card (int) : the number of the card chosen by the player.
    Returns:
        None 
    """
    paquet_card={"type":"card","card":card}
    for player in range (1, numberOfPlayers+1):
        if player !=player_num:
            mqSend(paquet_card, player)
    socketSend(paquet_card)
    resultat=socketReceive()
    if resultat=="Success":
        print("Success ! The card you chose fit on the board !")
    else:
        print("Oops, looks like this card could not fit on the board... Try again next time !")
 
def playCard():
    """
    Calls cardInput() to ask the user what card he wants to play, and sendCard()
    to send the card through the socket.
    Args:
        None
    Returns:
        None
    """
    print(f"What card do you want to play ? You have {infos_tour['tokens'][1]} fuse tokens left.")
    entree_card=cardInput()
 
    sendCard(entree_card)
    time.sleep(2)
 
def askClue():
    """
    Uses playerInput(), clueInput() and colorInput()/cardInput() to know
    what clue a player wants to send, and calls sendClue() to send the clue.
    Args:
        None
    Returns:
        None
    """
    entree_joueur = playerInput()
    #display_game()
    print(f"What type of clue do you want player {entree_joueur} to receive?")
    entree_classe = clueInput()
    if entree_classe=="color":
        #display_game()
        entree=colorInput(colors)
        entree_indice=colors.index(entree)
    else:
        #display_game()
        print(f"What number do you want to clue ? You have {infos_tour['tokens'][0]} information tokens left.")
        entree_indice=cardInput()
        print(f"Enter clue: {entree_indice}")
 
    sendClue(entree_joueur,entree_classe,entree_indice)
 
    time.sleep(2)
 
def socketReceive():
    """
    Receives messages through the socket.
    Args:
        None
    Returns:
        msg (string) : message received if no problem
                       -1 if an Exception was raised 
    """     
    try:
        msg = pickle.loads(socket.recv(1024))
    except Exception as e:
        print(f"Socket unreachable: ",e)
        try:
            socket.close()
        except:
            print("Socket already closed.")
        sys.exit()
        msg = "-1"
    return msg    
     
def socketSend(paquet):
    """
    Sends a message to a socket using pickle.
    Args:
        socket (socket.socket) : socket object representing the connection with a player.
        paquet (str/int/dict/list) : data to be sent to the player.
    Returns:
        None
    """
    try:
        socket.sendall(pickle.dumps(paquet))
    except Exception as e:
        print(f"Could not send paquet through the socket: ",e)

def mqReceive():
    """
    Receives a message whose recipient is the running process through the message queue.
    Args:
        None
    Returns:
        The received message loaded with pickles. 
    """
    try:
        #print("Starting msg reception via mq:")
        msg = mq.receive(type=player_num)
        return (pickle.loads(msg[0]))
    except Exception as e:
        print(f"Could not receive from mq: {e}")

def mqSend(paquet, id):
    """
    Sends a message to the right recipient through the message queue.
    Args:
        paquet (str/int/dict) : message to be sent 
        id (int) : id of the recipient player for the message
    Returns:
        None
    """
    try:
        #print(f"Sending message via mq: {paquet} to {id}")
        mq.send(pickle.dumps(paquet), type=id)
        #print(f"Sent msg {paquet} to {id}")
    except Exception as e:
        print(f"Could not send via mq: ",e)
        time.sleep(10)

def clear_terminal():
    """
    Clears the terminal using os module.
    Args:
        None
    Returns:
        None
    """
    os.system('clear')

def print_in_center(text):
    """
    Prints the text at the center of the screen according to the window size.
    Args:
        text lst str : string to be displayed
    Returns:
        None
    """
    print(f"\n{VOID_STYLE}")
    rows, columns = os.popen('stty size', 'r').read().split()
    vertical_padding = (int(rows) - len(text)) // 2

    for _ in range(vertical_padding):
        print()

    for line in text:
        horizontal_padding = (int(columns) - len(line)) // 2
        print(' ' * horizontal_padding + line)

    for _ in range(vertical_padding):
        print()

def print_in_center_top(text):
    """
    Prints the text at the center top of the screen according to the window size.
    Args:
        text lst str : string to be displayed
    Returns:
        None
    """
    _, columns = os.popen('stty size', 'r').read().split()

    for line in text:
        horizontal_padding = (int(columns) - len(line)) // 2
        print(' ' * horizontal_padding + line)

def print_in_center_top_two(text1, text2):
    """
    Prints two texts at the center top of the screen according to the window size.
    Args:
        text1 str : string to be displayed
        text2 str : string to be displayed
    Returns:
        None
    """
    _, columns = os.popen('stty size', 'r').read().split()

    padding1 = (int(columns)//2 - len(text1)) // 2
    padding2 = (int(columns)//2 - len(text2)) // 2
    print(' ' * padding1 + text1 + ' ' * padding1 + ' ' * padding2 + text2 + ' ' * padding2)

def waiting_screen():
    """
    Displays the waiting screen during the absence of an enough amount of players.
    Args:
        None
    Returns:
        None
    """
    # Has to be 1 second MAX
    print(f"{TEXT_WHITE}")
    animation = [
        ".  ",
        ".. ",
        "...",
        ]
    for c in animation:
        clear_terminal()
        text_to_print = text2art("Waiting\nfor\nplayers\n" + c, font='merlin1')
        print_in_center(text_to_print.split('\n'))
        time.sleep(0.3)
    print(f"{TEXT_BLACK}")

def display_welcome():
    """
    Displays the welcoming screen after the launch of the game.
    Args:
        None
    Returns:
        None
    """
    os.system(f'echo "\\033]0;Hannabis : Player {player_num}\\007"')
    clear_terminal()
    print(f"{TEXT_WHITE}")
    text_to_print = text2art("welcome\nto\nhannabis", font='merlin1')
    print_in_center(text_to_print.split('\n'))
    time.sleep(1)
    print(f"{TEXT_BLACK}")

def display_start():
    """
    Displays the starting screen after the amount of players required is reached.
    Args:
        None
    Returns:
        None
    """
    print(f"\n{VOID_STYLE}{TEXT_WHITE}")

    text_to_print = text2art("Game\nStarting\n", font='merlin1')
    print_in_center(text_to_print.split('\n'))
    time.sleep(2)

    tm = 3
    for i in range(tm):
        display_countdown(tm - i)

def display_countdown(num):
    """
    Displays the time left during the start.
    Args:
        num int : time left to display
    Returns:
        None
    """
    os.system('clear')
    text_to_print = text2art(str(num), font='merlin1')
    print_in_center(text_to_print.split('\n'))
    time.sleep(1)

def display_static_info():
    """
    Displays static informations such as the game title, key, player number, etc.
    Args:
        None
    Returns:
        None
    """
    left = f"You are Player {text2art(str(player_num), font='contouring1')}  with {numberOfPlayers - 1} other mates!"
    right = f"Access Key: {cle}"
    _, columns = os.popen('stty size', 'r').read().split()
    padding = (int(columns) - len(left) - len(right))

    print(f"{TEXT_WHITE}", end = "")
    print(left + ' ' * padding + right)
    text_to_print = text2art("hannabis", font='merlin1')
    print_in_center_top(text_to_print.split('\n'))
    print(f"{TEXT_BLACK}", end = "")

def display_boards(boards):
    """
    Displays static the current boards of the available colors.
    Args:
        board lst lst int : game's boards
    Returns:
        None
    """
    board_size = len("                                                       ")
    _, columns = os.popen('stty size', 'r').read().split()

    padding_center = (int(columns) - board_size) // 2
    padding_semi = (int(columns)//2 - board_size) // 2

    all_boards = [([],"",0)] * numberOfPlayers
    
    for i in range(numberOfPlayers):
        all_boards[i] = (boards[i],"Current " + colors[i] + " board :", i)
    
    lst = iter(all_boards)
    for (first_board, txt1, i1), (second_board, txt2, i2) in zip(lst, lst) :
        print_in_center_top_two(txt1, txt2)
        print()
        for i in range(6):
            print(f" " * padding_semi, end="")
            for j in range(5):
                if i == 5:
                    print(f"{VOID_STYLE}   {j + 1}   ", end="")
                elif first_board[j] == 1:
                    c = bg(colors[i1])
                    print(f"{c}       ", end="")
                else:
                    c = bg(color_dict['gray'])
                    print(f"{c}       ", end="")
                
                if j != 4 :
                    print(f"{VOID_STYLE}     ", end="")
                else :
                    print(f"{VOID_STYLE}", end="")
            print(f" " * padding_semi, end="")
            
                
            print(f" " * padding_semi, end="")
            for j in range(5):
                if i == 5:
                    print(f"{VOID_STYLE}   {j + 1}   ", end="")
                elif second_board[j] == 1:
                    c = bg(colors[i2])
                    print(f"{c}       ", end="")
                else:
                    c = bg(color_dict['gray'])
                    print(f"{c}       ", end="")
                
                if j != 4 :
                    print(f"{VOID_STYLE}     ", end="")
                else :
                    print(f"{VOID_STYLE}", end="")
            print()
        print()
    if numberOfPlayers % 2 == 1 :
        board, txt, k = all_boards[numberOfPlayers - 1]
        print_in_center_top([txt])
        for i in range(6):
            print(f" " * padding_center, end="")
            for j in range(5):
                if i == 5:
                    print(f"{VOID_STYLE}   {j + 1}   ", end="")
                elif board[j] == 1:
                    c = bg(colors[k])
                    print(f"{c}       ", end="")
                else:
                    c = bg(color_dict['gray'])
                    print(f"{c}       ", end="")
                
                if j != 4 :
                    print(f"{VOID_STYLE}     ", end="")
                else :
                    print(f"{VOID_STYLE}", end="")
            print()
        print()

def display_hand(hand):
    """
    Displays one single hand.
    Args:
        hand lst (int, int) : list of the hand's cards
    Returns:
        None
    """
    _, columns = os.popen('stty size', 'r').read().split()
    for i in range(6):
        padding = (int(columns) - 5 * len("       ") - len("     ")*4) // 2
        print(f" " * padding, end="")
        for j in range(len(hand)):
            num, color = hand[j]
            if i == 5:
                print(f"{VOID_STYLE}   {j + 1}   ", end="")
            elif color < 1:
                c = bg(color_dict['gray'])
                if num == -1 :
                    print(f"{c}       ", end="")
                else :
                    if i != 2:
                        print(f"{c}       ", end="")
                    else:
                        print(f"{c}   {TEXT_WHITE}{num}{TEXT_BLACK}   ", end="")
            else:
                c = bg(color_dict[colors[color - 1]])
                if num == -1 :
                    print(f"{c}       ", end="")
                elif i != 2:
                    print(f"{c}       ", end="")
                else:
                    print(f"{c}   {TEXT_WHITE}{num}{TEXT_BLACK}   ", end="")
            
            if j != 4 :
                print(f"{VOID_STYLE}     ", end="")
            else :
                print(f"{VOID_STYLE}", end="")
        print()

def display_players_hands():
    """
    Displays the players' hand, aligned with each others.
    Args:
        None
    Returns:
        None
    """
    hand_size = len("                                                       ")
    _, columns = os.popen('stty size', 'r').read().split()

    padding_center = (int(columns) - hand_size) // 2
    padding_semi = (int(columns)//2 - hand_size) // 2

    all_hands = [([],"")] * numberOfPlayers
    your_hand = []
    for card in infos_tour['infos_decks'][str(player_num)]:
        color = card[1].index(1) + 1
        if color == 1 and card[1][1] == 1 :
            color = -1
        num = -1
        for i in card[0] :
            if i != 0 :
                num = i 
        if card[0][num - 1] == card[0][num] :
            num = -1
        your_hand.append((num,color))

    all_hands[player_num - 1] = (your_hand, "Your hand :")
    for player,hand in infos_tour["hands"].items():
        all_hands[int(player) - 1] = (hand,"Player " + player + "'s hand :")
    
    lst = iter(all_hands)
    for (first_hand, txt1), (second_hand, txt2) in zip(lst, lst) :
        print_in_center_top_two(txt1, txt2)
        print()
        for i in range(6):
            print(f" " * padding_semi, end="")
            for j in range(5):
                num, color = first_hand[j]
                if i == 5:
                    print(f"{VOID_STYLE}   {j + 1}   ", end="")
                elif color < 1:
                    c = bg(color_dict['gray'])
                    if num == -1 :
                        print(f"{c}       ", end="")
                    else :
                        if i != 2:
                            print(f"{c}       ", end="")
                        else:
                            print(f"{c}   {TEXT_WHITE}{num}{TEXT_BLACK}   ", end="")
                else:
                    c = bg(color_dict[colors[color - 1]])
                    if num == -1 :
                        print(f"{c}       ", end="")
                    elif i != 2:
                        print(f"{c}       ", end="")
                    else:
                        print(f"{c}   {TEXT_WHITE}{num}{TEXT_BLACK}   ", end="")
                if j != 4 :
                    print(f"{VOID_STYLE}     ", end="")
                else :
                    print(f"{VOID_STYLE}", end="")
            print(f" " * padding_semi, end="")
            
                
            print(f" " * padding_semi, end="")
            for j in range(5):
                num, color = second_hand[j]
                if i == 5:
                    print(f"{VOID_STYLE}   {j + 1}   ", end="")
                elif color < 1:
                    c = bg(color_dict['gray'])
                    if num == -1 :
                        print(f"{c}       ", end="")
                    else :
                        if i != 2:
                            print(f"{c}       ", end="")
                        else:
                            print(f"{c}   {TEXT_WHITE}{num}{TEXT_BLACK}   ", end="")
                else:
                    c = bg(color_dict[colors[color - 1]])
                    if num == -1 :
                        print(f"{c}       ", end="")
                    elif i != 2:
                        print(f"{c}       ", end="")
                    else:
                        print(f"{c}   {TEXT_WHITE}{num}{TEXT_BLACK}   ", end="")
                if j != 4 :
                    print(f"{VOID_STYLE}     ", end="")
                else :
                    print(f"{VOID_STYLE}", end="")
            print()
        print()
    if numberOfPlayers % 2 == 1 :
        hand, txt = all_hands[numberOfPlayers - 1]
        print_in_center_top([txt])
        display_hand(hand)

def display_game():
    """
    Launch of the different overlays. 
    Args:
        None
    Returns:
        None
    """
    board = infos_tour['game_board']
    clear_terminal()
    display_static_info()
    display_boards(board)
    display_players_hands()
 
if __name__ == '__main__':
    HOST = "localhost"
    PORT = 6666
    playing = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:  
        socket.connect((HOST, PORT))
 
        infos_depart=socketReceive()
        player_num=infos_depart["player_num"]
        cle=infos_depart["queue_key"]
        numberOfPlayers=infos_depart["numberOfPlayers"]
 
        mq = sysv_ipc.MessageQueue(cle) 
        colors=colors[:numberOfPlayers]
    
        display_welcome()

        message=socketReceive()
        while message == "Waiting for players...":
            waiting_screen()
            message=socketReceive()
        
        display_start()
 
        while playing:
            infos_tour=socketReceive()
            
            display_game()
            #  print(infos_tour)
            if "EOG" in infos_tour:
                print(f"Uh oh, the game is about to end. Play your last turn !\n {infos_tour['Reason_EOG']}")
                playing = False
            
            elif "game_board" in infos_tour:   
                if infos_tour["turn"]==player_num:
                    if infos_tour['tokens'][0]!=0:
                        print(f"It's your turn to play. You have {infos_tour['tokens'][0]} information tokens and {infos_tour['tokens'][1]} fuse tokens left.\n")
                        entree=moveInput()
                    else:
                        print("Uh oh, looks like there are no information tokens left, try playing a card...")
                        entree=moveInput()
 
                    if entree==1:
                        #display_game()
                        playCard()
                    else:
                        #display_game()
                        askClue()

                    socketSend("End of Turn")
    
                else:
                    print(f"It is player {infos_tour['turn']}'s turn.")
                    paquet=mqReceive()
                    #print(f"Received paquet: {paquet}")

                    if paquet == -1:
                        break
                    elif paquet["type"]=="indice":
                        indice = colors[paquet['indice']] if paquet['classe'] == 'color' else paquet['indice']
                        if int(paquet["joueur"])==player_num:
                            print(f"{infos_tour['turn']} just gave you a clue about {paquet['classe']} {indice} !")
                        else:
                            print(f"{infos_tour['turn']} sent a clue to {paquet['joueur']} about {paquet['classe']} {indice} !")
                    elif paquet["type"]=="card":
                        print(f"{infos_tour['turn']} just played card n°{paquet['card']}")
  
    print("Closing game.")