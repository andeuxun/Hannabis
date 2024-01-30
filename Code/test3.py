from colored import fg, bg, attr
from art import text2art
import os
import time

# Define color and style constants
color_dict = {
    "blue": 17,
    "red": 124,
    "green": 28,
    "yellow": 184,
    "orange": 215,
    "purple": 54,
    "black": 0,
    "white": 15,
    "gray": 242,
}

colors = ["blue", "red", "green", "yellow", "orange", "purple"]

VOID_STYLE = bg('steel_blue')
TEXT_WHITE = fg("white") + attr("bold")
TEXT_BLACK = fg("black")

print(f"\n{VOID_STYLE}")

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

def waiting_screen():
    print(f"{TEXT_WHITE}")
    animation = [
        " |=         |",
        " | =        |",
        " |  =       |",
        " |   =      |",
        " |    =     |",
        " |     =    |",
        " |      =   |",
        " |       =  |",
        " |        = |",
        " |         =|",
        " |        = |",
        " |       =  |",
        " |      =   |",
        " |     =    |",
        " |    =     |",
        " |   =      |",
        " |  =       |",
        " | =        |",
        ]
    for c in animation:
        clear_terminal()
        text_to_print = text2art("Waiting\nfor\nplayers\n" + c, font='ghost')
        print_in_middle(text_to_print.split('\n'))
        time.sleep(0.1)
    print(f"{TEXT_BLACK}")

def display_welcome():
    print(f"{TEXT_WHITE}")
    text_to_print = text2art("welcome\nto\nhannabis", font='ghost')
    print_in_middle(text_to_print.split('\n'))
    time.sleep(2)
    print(f"{TEXT_BLACK}")

def display_start():
    print(f"\n{VOID_STYLE}{TEXT_WHITE}")

    # Display text art centered vertically
    text_to_print = text2art("Game\nStarting\n", font='lildevil')
    print_in_middle(text_to_print.split('\n'))
    time.sleep(2)

    # Countdown animation
    for i in range(5):
        display_countdown(5 - i)

def display_countdown(number):
    os.system('clear')
    text_to_print = text2art(str(number), font='lildevil')
    print_in_middle(text_to_print.split('\n'))
    time.sleep(1)

def display_static_info():
    left = f"You are Player {text2art(str(num_player), font='contouring1')}  with {nb_players - 1} other mates!"
    right = f"Access Key: {key}"
    _, columns = os.popen('stty size', 'r').read().split()
    padding = (int(columns) - len(left) - len(right))
    print(left + ' ' * padding + right)

    print(f"{TEXT_WHITE}")
    text_to_print = text2art("hannabis", font='ghost')
    print_in_middle_top(text_to_print.split('\n'))
    print(f"{TEXT_BLACK}")

    padding = (int(columns) - len(colors) * len("          "))

def display_board(board):
    _, columns = os.popen('stty size', 'r').read().split()
    padding = (int(columns) - len(colors) * len("          ") - 5 * len("            ")) // 2

    txt_color = "Available colors"
    txt_board = "Current board"
    temp_padding = (5 * len("            ") - len(txt_board))//2
    print(f" " * (padding + temp_padding), end="")
    print(f"{txt_board}", end="")
    print(f" " * (temp_padding), end="")


    temp_padding = (len(colors) * len("          ") - len(txt_color)) // 2
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
            print(f"{VOID_STYLE}     ", end="")
        print(f" " * padding, end="")

        for color in colors:
            c = bg(color_dict[color])
            if i == 5:
                print(f"{color}", end="")
                print(f"{VOID_STYLE}     ", end="")
            else:
                print(f"{c}      ", end="")
                print(f"{VOID_STYLE}    ", end="")
        print()

def display_hand(hand):
    _, columns = os.popen('stty size', 'r').read().split()
    padding = (int(columns) - 5 * (len("       ") + len("     "))) // 2
    for i in range(6):
        print(f" " * padding, end="")
        for j in range(5):
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
                    print(f"{c}   {fg('black') + bg(color_dict[colors[color - 1]])}{num}{c}   ", end="")
            print(f"{VOID_STYLE}     ", end="")
        print()

def main():
    clear_terminal()
    print(f"\n{VOID_STYLE}") 

    display_welcome()
    clear_terminal()

    while(True):
        waiting_screen()
        break

    display_start()
    clear_terminal()


    display_static_info()
    board = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    display_board(board)

    display_hand([(1,1),(2,3),(0,0),(4,2),(5,5)])

if __name__ == "__main__":
    num_player = 2
    key = 157   
    nb_players = 5
    main()
