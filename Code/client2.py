# client
import socket
import sysv_ipc
import time
from multiprocessing import Process, Manager, Pipe
import json
import pickle
import os
from colored import bg, fg, attr
from art import *
 
global playing

color_dict = {
    "blue": 23,
    "red": 124,
    "green": 106,
    "orange": 215,
    "yellow": 184,
    "purple": 54,
    "black": 0,
    "white": 15,
    "gray": 242,
}

colors = ["blue", "red", "green", "yellow", "orange", "purple"]

VOID_STYLE = bg('steel_blue')
TEXT_WHITE = fg("white") + attr("bold")
TEXT_BLACK = fg("black")

print(f"{VOID_STYLE}")

 
def cardInput():
    while True:
        entree = input(f"\nSelect a number from 1 to 5 : ")
        try:
            if 1 <= int(entree) <= 5:
                return int(entree)
        except:
            print("Invalid input.\n")
            continue
 
def playerInput():
    while True:
        entree = input(f"\nWhich player do you want to send the clue to ?\n\nEnter a number between 1 and {numberOfPlayers} : ")
        try:
            if 1 <= int(entree) <= numberOfPlayers and int(entree) != player_num:
                return int(entree)
        except:
            print("Invalid input.\n")
            continue
 
def clueInput():
    while True:
        entree = input(f"\nDo you want to give a color clue or a number clue ?\n\nPlease type 'color' or 'number' : ")
        try:
            if entree == 'color' or entree == 'number':
                return entree
        except:
            print("Invalid input.\n")
 
def colorInput(colors):
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
    while True:
        entree = input(f"Choose a move:\n     1.Play a card\n     2.Give a clue\n")
        try:
            if int(entree) == 1 or int(entree) == 2:
                return int(entree)
        except:
            print("Invalid input. Please enter a number between 1 and 2.")
 
def sendClue(joueur, classe, indice):
    paquet_indice={"type":"indice", "joueur":str(joueur), "classe":classe,"indice":indice}
    for player_num in range (1, numberOfPlayers+1):
        if player_num!=player_num:
            mq_send(paquet_indice, player_num)
    socket_send(paquet_indice)
 
def sendCard(card):
    paquet_card={"type":"card","card":card}
    for player_num in range (1, numberOfPlayers+1):
        if player_num!=player_num:
            mq_send(paquet_card, player_num)
    socket_send(paquet_card)
    resultat=socket_receive()
    if resultat=="Success":
        print("Success ! The card you chose fit on the board !")
    else:
        print("Oops, looks like this card could not fit on the board... Try again next time !")
 
def playCard():
    print(f"What card do you want to play ? You have {infos_tour['tokens'][1]} fuse tokens left.")
    entree_card=cardInput()
 
    sendCard(entree_card)
    time.sleep(2)
 
def donnerIndice():
    entree_joueur = playerInput()
    display_game()
    print(f"What type of clue do you want player {entree_joueur} to receive?")
    entree_classe = clueInput()
    if entree_classe=="color":
        display_game()
        entree=colorInput(colors)
        entree_indice=colors.index(entree)
    else:
        display_game()
        print(f"What number do you want to clue ? You have {infos_tour['tokens'][0]} information tokens left.")
        entree_indice=cardInput()
        print(f"Enter clue: {entree_indice}")
 
    sendClue(entree_joueur,entree_classe,entree_indice)
 
    time.sleep(2)
 
def socket_receive():
    try:
        msg = pickle.loads(socket.recv(1024))
    except Exception as e:
        print(f"Socket unreachable: ",e)
        msg = "-1"
    return msg    
 
def socket_send(paquet):
    socket.sendall(pickle.dumps(paquet))
 
def mq_receive():
    return (pickle.loads((mq.receive(type=player_num))[0]))
 
def mq_send(paquet, id):
    mq.send(pickle.dumps(paquet), type=id)

def clear_terminal():
    os.system('clear')

def print_in_middle(lines):
    print(f"\n{VOID_STYLE}")
    rows, columns = os.popen('stty size', 'r').read().split()
    vertical_padding = (int(rows) - len(lines)) // 2

    for _ in range(vertical_padding):
        print()

    for line in lines:
        horizontal_padding = (int(columns) - len(line)) // 2
        print(' ' * horizontal_padding + line)

    for _ in range(vertical_padding):
        print()

def print_in_middle_top(text):
    _, columns = os.popen('stty size', 'r').read().split()

    for line in text:
        horizontal_padding = (int(columns) - len(line)) // 2
        print(' ' * horizontal_padding + line)

def print_in_middle_top_two(text1, text2):
    _, columns = os.popen('stty size', 'r').read().split()

    padding1 = (int(columns)//2 - len(text1)) // 2
    padding2 = (int(columns)//2 - len(text2)) // 2
    print(' ' * padding1 + text1 + ' ' * padding1 + ' ' * padding2 + text2 + ' ' * padding2)

def waiting_screen():
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
        print_in_middle(text_to_print.split('\n'))
        time.sleep(0.3)
    print(f"{TEXT_BLACK}")

def display_welcome():
    os.system(f'echo "\\033]0;Hannabis : Player {player_num}\\007"')
    print(f"{TEXT_WHITE}")
    text_to_print = text2art("welcome\nto\nhannabis", font='merlin1')
    print_in_middle(text_to_print.split('\n'))
    time.sleep(1)
    print(f"{TEXT_BLACK}")

def display_start():
    print(f"\n{VOID_STYLE}{TEXT_WHITE}")

    # Display text art centered vertically
    text_to_print = text2art("Game\nStarting\n", font='merlin1')
    print_in_middle(text_to_print.split('\n'))
    time.sleep(2)

    # Countdown animation
    tm = 3
    for i in range(tm):
        display_countdown(tm - i)

def display_countdown(num):
    os.system('clear')
    text_to_print = text2art(str(num), font='merlin1')
    print_in_middle(text_to_print.split('\n'))
    time.sleep(1)

def display_static_info():
    left = f"You are Player {text2art(str(player_num), font='contouring1')}  with {numberOfPlayers - 1} other mates!"
    right = f"Access Key: {cle}"
    _, columns = os.popen('stty size', 'r').read().split()
    padding = (int(columns) - len(left) - len(right))

    print(f"{TEXT_WHITE}", end = "")
    print(left + ' ' * padding + right)
    text_to_print = text2art("hannabis", font='merlin1')
    print_in_middle_top(text_to_print.split('\n'))
    print(f"{TEXT_BLACK}", end = "")

def display_board(board):
    _, columns = os.popen('stty size', 'r').read().split()
    padding = (int(columns) - (len(colors) * len("       ") + (len(colors) - 1) * len("     ")) - (5 * len("       ") + 4 * len("     "))) // 2

    txt_color = "Available colors"
    txt_board = "Current board"
    temp_padding = ((5 * len("       ") + 4 * len("     ")) - len(txt_board))//2
    print(f" " * (padding + temp_padding), end="")
    print(f"{txt_board}", end="")
    print(f" " * (temp_padding), end="")

    temp_padding = ((len(colors) * len("       ") + (len(colors) - 1) * len("     ")) - len(txt_color)) // 2
    print(f" " * (padding + temp_padding), end="")
    print(f"{txt_color}")
    print()

    for i in range(6):
        print(f" " * padding, end="")

        for j in range(5):
            num, color = board[0][j], board[1][j]
            if i == 5:
                print(f"{VOID_STYLE}   {j + 1}   ", end="")
            elif color < 1:
                c = bg(color_dict['gray'])
                print(f"{c}       ", end="")
            else:
                c = fg(color_dict[colors[color - 1]]) + bg(color_dict[colors[color - 1]])
                if i != 2:
                    print(f"{c}       ", end="")
                else:
                    print(f"{c}   {fg('black') + bg(color_dict[colors[color - 1]])}{num}{c}   ", end="")
            
            if j != 4 :
                print(f"{VOID_STYLE}     ", end="")
            else :
                print(f"{VOID_STYLE}", end="")

        print(f" " * (padding ), end="")
        for color in colors:
            c = bg(color_dict[color])
            if i == 5:
                print(f"{color}", end="")
                print(f"{VOID_STYLE}     ", end="")
            else:
                print(f"{c}      ", end="")
                print(f"{VOID_STYLE}    ", end="")
        print()
    print()

def display_hand(hand):
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
                print(f"{c}       ", end="")
            else:
                c = bg(color_dict[colors[color - 1]])
                if i != 2:
                    print(f"{c}       ", end="")
                else:
                    print(f"{c}   {TEXT_WHITE}{num}{TEXT_BLACK}   ", end="")
            
            if j != 4 :
                print(f"{VOID_STYLE}     ", end="")
            else :
                print(f"{VOID_STYLE}", end="")
        print()

def display_players_hands():
    hand_size = len("                                                       ")
    _, columns = os.popen('stty size', 'r').read().split()

    padding_center = (int(columns) - hand_size) // 2
    padding_semi = (int(columns)//2 - hand_size) // 2

    all_hands = [([],"")] * numberOfPlayers
    your_hand = []
    for card in infos_tour['infos_decks'][str(player_num)]:
        num = card[0].index(1)
        color = card[1].index(1)
        if num == 0 and card[0][1] == 1 :
            num = -1
        if color == 0 and card[1][1] == 1 :
            color = -1
        your_hand.append((num,color))

    all_hands[player_num - 1] = (your_hand, "Your hand :")
    for player,hand in infos_tour["hands"].items():
        all_hands[int(player) - 1] = (hand,"Player " + player + "'s hand :")
    
    lst = iter(all_hands)
    for (first_hand, txt1), (second_hand, txt2) in zip(lst, lst) :
        print_in_middle_top_two(txt1, txt2)
        print()
        for i in range(6):
            print(f" " * padding_semi, end="")
            for j in range(5):
                num, color = first_hand[j]
                if i == 5:
                    print(f"{VOID_STYLE}   {j + 1}   ", end="")
                elif color < 1:
                    c = bg(color_dict['gray'])
                    print(f"{c}       ", end="")
                else:
                    c = bg(color_dict[colors[color - 1]])
                    if i != 2:
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
                    print(f"{c}       ", end="")
                else:
                    c = bg(color_dict[colors[color - 1]])
                    if i != 2:
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
        print_in_middle_top([txt])
        display_hand(hand)

def display_game():
    board = infos_tour['game_board']
    clear_terminal()
    display_static_info()
    display_board(board)
    display_players_hands()

if __name__ == '__main__':
    HOST = "localhost"
    PORT = 6666
    playing = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:  
        socket.connect((HOST, PORT))
 
        infos_depart=socket_receive()
        player_num=infos_depart["player_num"]
        cle=infos_depart["queue_key"]
        numberOfPlayers=infos_depart["numberOfPlayers"]

        mq = sysv_ipc.MessageQueue(cle)
        colors=colors[:numberOfPlayers]

        clear_terminal()
        display_welcome()
 
        message=socket_receive()
        while message == "Waiting for players...":
            waiting_screen()
            message=socket_receive()
        
        display_start()
        
        # Début du premier tour
        while playing:
            infos_tour=socket_receive()
            display_game()
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
                        display_game()
                        playCard()
                    else:
                        display_game()
                        donnerIndice()
 
                    socket_send("End of Turn")
 
                else:
                    print(f"It is player {infos_tour['turn']}'s turn.")
                    paquet=mq_receive()
                    if paquet == -1:
                        break
                    elif paquet["type"]=="indice":
                        # article = "la" if paquet['classe'] == 'color' else "le"
                        indice = colors[paquet['indice']] if paquet['classe'] == 'color' else paquet['indice']
                        if int(paquet["joueur"])==player_num:
                            print(f"{infos_tour['turn']} just gave you a clue about {paquet['classe']} {indice} !")
                        else:
                            print(f"{infos_tour['turn']} sent a clue to {paquet['joueur']} about {paquet['classe']} {indice} !")
                    elif paquet["type"]=="card":
                        print(f"{infos_tour['turn']} just played card n°{paquet['card']}")
    print("Closing game.")