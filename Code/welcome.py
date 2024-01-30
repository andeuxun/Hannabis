from colored import fg, bg, attr
from art import text2art
import os
import time

# Define color and style constants
VOID_STYLE = bg('steel_blue')
CARDS_STYLE = bg("#0000FF") + fg("white")
TEXT_WHITE = fg("white") + attr("bold")
TEXT_BLACK = fg("black")

BOLD_STYLE = attr("bold")
RESET_STYLE = attr("reset")
print(f"\n{VOID_STYLE}{TEXT_WHITE}")
# Function to print in the middle of the terminal
def print_in_middle(lines):
    rows, columns = os.popen('stty size', 'r').read().split()
    vertical_padding = (int(rows) - len(lines)) // 2

    for _ in range(vertical_padding):
        print()

    for line in lines:
        horizontal_padding = (int(columns) - len(line)) // 2
        print(' ' * horizontal_padding + line)

    for _ in range(vertical_padding):
        print()

# Clear the terminal
os.system('clear')

# Display text art centered vertically
text_to_print = text2art("Game\nStarting\n", font='lildevil')
print_in_middle(text_to_print.split('\n'))
time.sleep(2)

# Countdown animation
for i in range(5):
    os.system('clear')
    text_to_print = text2art(str(5 - i), font='lildevil')
    print_in_middle(text_to_print.split('\n'))
    time.sleep(1)
