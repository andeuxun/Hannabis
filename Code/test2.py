from colored import fg, bg, attr
from art import text2art
import os
import time
'''''
sandy_brown : orange sympa
'''''

# Define color and style constants
color_dict = {
    "blue" : 17, 
    "red" : 124, 
    "green" : 28, 
    "yellow" : 184, 
    "orange" : 215, 
    "purple" : 54,
    "black" : 0, 
    "white" : 15,  
    "gray" : 242, 
}

colors = [
    "blue", 
    "red", 
    "green", 
    "yellow", 
    "orange", 
    "purple", 
]
VOID_STYLE = bg('steel_blue')
CARDS_STYLE = bg("#0000FF") + fg("white")
TEXT_WHITE = fg("white") + attr("bold")
TEXT_BLACK = fg("black")

BOLD_STYLE = attr("bold")
RESET_STYLE = attr("reset")

num_player = 2
key = 157
nb_players = 5
print(f"\n{VOID_STYLE}")

# Function to print in the middle of the terminal
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
    # Get terminal size
    _, columns = os.popen('stty size', 'r').read().split()

    # Print horizontal padding and the text in the middle
    for line in text:
        horizontal_padding = (int(columns) - len(line)) // 2
        print(' ' * horizontal_padding + line)

# Clear the terminal
os.system('clear')


# Display Welcome To Hannabis 
#NICE FONT rammstein / merlin1 / lildevil / ghost
print(f"{TEXT_WHITE}")
text_to_print = text2art("welcome\nto\nhannabis", font='ghost')
print_in_middle(text_to_print.split('\n'))
time.sleep(2)
print(f"{TEXT_BLACK}")

# Display static info : Title, Player number, key, colors available, nb of player
os.system('clear')

left = "You are Player " + text2art(str(num_player), font='contouring1') + "with" + str(nb_players - 1) + "other mates !"
right = "Access Key : " + str(key)
_, columns = os.popen('stty size', 'r').read().split()
padding = (int(columns) - len(left) - len(right))
print(left + ' ' * padding + right)

print(f"{TEXT_WHITE}")
text_to_print = text2art("hannabis", font='ghost')
print_in_middle_top(text_to_print.split('\n'))
print(f"{TEXT_BLACK}")

padding = (int(columns) - len(colors)*len("          "))

txt = "Available colors"
temp_padding = (len(colors)*len("          ") - len(txt))//2
print(f" "*(temp_padding + padding), end="")
print(txt)
for i in range(6):
    print(f" "*padding, end="")
    for color in colors:
        c = bg(color_dict[color])
        if i == 5 :
            print(f"{color}", end="")
            print(f"{VOID_STYLE}     ", end="")
        else :
            print(f"{c}      ", end="")
            print(f"{VOID_STYLE}    ", end="")
    print()

# Plateau
board = [[0,0,0,0,0],[0,0,0,0,0]]
padding = (int(columns) - len(colors)*len("          ") - 5*len("          "))//2 #mm paddint quavnat
for i in range(5):
    print(f" "*padding, end="")
    for j in range(5):
        num,color = board[0][j],board[1][j]
        if color < 1 :
            c = bg(color_dict['gray'])
            print(f"{c}      ", end="")
        else : 
            c = fg(color_dict[colors[color - 1]]) + bg(color_dict[colors[color - 1]])
            if i != 2:
                print(f"{c}███████", end="")
            else:
                print(f"{c}███{fg('black') + bg(color_dict[colors[color - 1]])}{num}{c}███", end="")
        print(f"{VOID_STYLE}    ", end="")
    print()
print(f" "*padding, end="")
for j in range(5):
    print(f"{VOID_STYLE}   {j + 1}      ", end="")

print(f"\n{VOID_STYLE}")






time.sleep(100)




# Countdown animation
for i in range(5):
    os.system('clear')
    text_to_print = text2art(str(5 - i), font='ghost')
    print_in_middle(text_to_print.split('\n'))
    time.sleep(1)
