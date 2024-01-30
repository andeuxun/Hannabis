from colored import fg, bg, attr
from art import text2art
import os
import time

print()
_, column = os.popen('stty size', 'r').read().split()
padding = (int(column) - 10 * (len("     ") + len("    "))) // 2
for color in range(25):
    for i in range(6):
        print(f"{bg('grey_3')} "*padding, end="")
        k = 0
        for j in range(10):
            c = bg(color*10 + k)
            if i == 5 :
                print(f"{fg('white')}   {color*10 + k}  ", end="")
            else :
                print(f"{c}     ", end="")

            print(f"{bg('black')}    ", end="")
            k += 1
        print()

    print()
    print()

    