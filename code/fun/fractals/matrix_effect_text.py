MAX_CASCADES = 600
MAX_COLS = 20
FRAME_DELAY = 0.03
MAX_SPEED = 5

import shutil, sys, time, os
from random import choice, randrange, paretovariate

CSI = "\x1b["
pr = lambda command: print("\x1b[", command, sep="", end="")

black, green, white = "30", "32", "37"

def getchars(start, end):
    return [chr(i) for i in range(start, end)]

# Character sets
latin = getchars(0x30, 0x80)
greek = getchars(0x390, 0x3d0)
hebrew = getchars(0x5d0, 0x5eb)
cyrillic = getchars(0x400, 0x500)

# Matrix-style extras
extra = list("ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ0123456789@#$%^&*abcdefghijklmnopqrstuvwxyz"
             "あいうえおかきくけこさしすせそたちつてと"
             "なにぬねのはひふへほまみむめもやゆよらりるれろわをん"
             "ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ")

# Combine and deduplicate
chars = list(dict.fromkeys(latin + greek + hebrew + cyrillic + extra))

def pareto(limit):
    scale = lines // 2
    number = (paretovariate(1.16) - 1) * scale
    return max(0, limit - number)

def init():
    global cols, lines
    try:
        if os.name == 'nt':  # Windows terminal size boost
            os.system("mode con: cols=300 lines=100")
    except:
        pass
    cols, lines = shutil.get_terminal_size()
    pr("?25l")  # Hide cursor
    pr("s")     # Save cursor position

def end():
    pr("m")     # Reset attributes
    pr("2J")    # Clear screen
    pr("u")     # Restore cursor
    pr("?25h")  # Show cursor

def print_at(char, x, y, color="", bright="0"):
    pr("%d;%df" % (y, x))
    pr(bright + ";" + color + "m")
    print(char, end="", flush=True)

def update_line(speed, counter, line):
    counter += 1
    if counter >= speed:
        line += 1
        counter = 0
    return counter, line

def cascade(col):
    speed = randrange(1, MAX_SPEED)
    espeed = randrange(1, MAX_SPEED)
    line = counter = ecounter = 0
    oldline = eline = -1
    erasing = False
    bright = "1"
    limit = pareto(lines)
    while True:
        counter, line = update_line(speed, counter, line)
        if randrange(10 * speed) < 1:
            bright = "0"
        if line > 1 and line <= limit and oldline != line:
            print_at(choice(chars), col, line - 1, green, bright)
        if line < limit:
            print_at(choice(chars), col, line, white, "1")
        if erasing:
            ecounter, eline = update_line(espeed, ecounter, eline)
            print_at(" ", col, eline, black)
        else:
            erasing = randrange(line + 1) > (lines / 2)
            eline = 0
        yield None
        oldline = line
        if eline >= limit:
            print_at(" ", col, oldline, black)
            break

def main():
    cascading = set()
    while True:
        while add_new(cascading): pass
        stopped = iterate(cascading)
        sys.stdout.flush()
        cascading.difference_update(stopped)
        time.sleep(FRAME_DELAY)

def add_new(cascading):
    if randrange(MAX_CASCADES + 1) > len(cascading):
        col = randrange(cols)
        for i in range(randrange(MAX_COLS)):
            cascading.add(cascade((col + i) % cols))
        return True
    return False

def iterate(cascading):
    stopped = set()
    for c in cascading:
        try:
            next(c)
        except StopIteration:
            stopped.add(c)
    return stopped

def doit():
    try:
        init()
        main()
    except KeyboardInterrupt:
        pass
    finally:
        end()

if __name__ == "__main__":
    doit()
