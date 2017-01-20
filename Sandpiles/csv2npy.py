'''
covert the csv output of the sandpile.go program to numpy .npy format
'''
import sys
import os
import numpy as np


def trim_grid(grid):
    # Trim empty
    grid = [r for r in grid if sum(r) > 0]
    # Trim empty columns
    w1 = len(grid[0])
    trans = [[r[n] for r in grid] for n in range(w1)]
    trans = [r for r in trans if sum(r) > 0]
    w2 = len(trans[0])
    grid = [[r[n] for r in trans] for n in range(w2)]

    return np.array(grid)


should_trim = sys.argv[1]

for _, _, files in os.walk("csv/"):
    for fname in files:
        csv_data = np.genfromtxt("csv/{}".format(fname), delimiter=",")
        csv_data = trim_grid(csv_data)
        np.save("npy/{}".format(fname[:-4]), csv_data)
