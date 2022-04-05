import subprocess
import sys
import time
from datetime import datetime
#import threading
import os
from PIL import Image
import numpy as np

top_left = (93, 885)
pitch = ((834-93)//3, (1623-885)//3)
number = {
    (212, 205, 197, 255): 0,
    (236, 228, 219, 255): 2,
    (235, 224, 202, 255): 4,
    (232, 180, 129, 255): 8,
    (231, 153, 108, 255): 16,
    (230, 131, 103, 255): 32,
    (228, 104, 71, 255): 64,
    (232, 208, 127, 255): 128,
    (231, 205, 114, 255): 256,
    (231, 201, 101, 255): 512,
}

def threadclick(xy, t=300):
    x, y = xy
    #return subprocess.run(["adb", "shell",  "input", "tap", f"{x}", f"{y}"])
    threading.Thread(
        target=subprocess.run,
        args=(["adb", "shell", "input", "swipe", f"{x}", f"{y}", f"{x}", f"{y}", f"{t}"],),
    )

def swipe(direction, t=300):
    print(direction)
    midx, midy = top_left[0] + 1.5*pitch[0], top_left[1] + 1.5*pitch[1]
    to_x, to_y = midx, midy
    swipe_d = pitch[0] * 2.5
    if direction=="left":
        to_x -= swipe_d
    elif direction=="right":
        to_x += swipe_d
    elif direction=="down":
        to_y += swipe_d
    elif direction=="up":
        to_y -= swipe_d
    subprocess.run(["adb", "shell", "input", "swipe", f"{midx}", f"{midy}", f"{to_x}", f"{to_y}", f"{t}"])

def getscreen():
    os.system("adb exec-out screencap -p > shot.png")

def getstatus():
    """Gets the status of the game as a 4x4 list."""
    getscreen()
    im = Image.open("shot.png")
    status = []
    for i in range(4):
        status.append([])
        for j in range(4):
            pix = im.getpixel((top_left[0] + j*pitch[0], top_left[1] + i*pitch[1]))
            if pix not in number:
                print(f"{pix} at {(i, j)} not in number!")
            status[i].append(number[pix])
    def pairvals(a, b, c, d):
        pairs = []
        if (b == a or b == c) and b != 0:
            pairs.append(b)
        if c == d and c != 0:
            pairs.append(c)
        return pairs
    def freedom(a, b, c, d):
        """can we slide a towards d?"""
        return (
            (d==0 and (a or b or c)) or
            (c==0 and (a or b)) or
            (b==0 and a)
        )
    def freedomrows(rows):
        return (
            freedom(*rows[0]) or
            freedom(*rows[1]) or
            freedom(*rows[2]) or
            freedom(*rows[3])
        )
    horizontals = []
    for i in range(4):
        horizontals += pairvals(*status[i])
    verticals = []
    for i in range(4):
        verticals += pairvals(*[status[k][i] for k in range(4)])
    freedoms = {
        "right": freedomrows(status) or len(horizontals),
        "left": freedomrows([s[::-1] for s in status]) or len(horizontals),
        "down": freedomrows([[s[k] for s in status] for k in range(4)]) or len(verticals),
        "up": freedomrows([[s[k] for s in status][::-1] for k in range(4)]) or len(verticals),
    }
    return status, verticals, horizontals, freedoms

def down_right(n=1):
    for _ in range(n):
        swipe("down")
        swipe("right")

def down_right_greedy():
    while True:
        status, verts, horis, freedoms = getstatus()
        if verts or horis:
            maxv = 0 if not verts else np.max(verts)
            maxh = 0 if not horis else np.max(horis)
            if maxv > maxh:
                swipe("down")
            else:
                swipe("right")
        for d in ["down", "right", "left", "up"]:
            if freedoms[d]:
                swipe(d)
                break

down_right_greedy()
