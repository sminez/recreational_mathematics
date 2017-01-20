import numpy as np
import seaborn as sns
from time import time
from subprocess import run
from matplotlib import animation
from matplotlib import pyplot as plt


class SandHeap:
    '''Control class for managaing sandpile topples'''
    patterns = {
            '+': {
                'maxval': 4,
                'topple_cells': [(-1, 0), (1, 0), (0, -1), (0, 1)]
                },
            'x': {
                'maxval': 4,
                'topple_cells': [(-1, 1), (-1, -1), (1, 1), (1, -1)]
                },
            'o': {
                'maxval': 8,
                'topple_cells': [
                    (-1, 0), (1, 0), (0, -1), (0, 1),
                    (-1, 1), (-1, -1), (1, 1), (1, -1)
                    ]
                },
            '++': {
                'maxval': 8,
                'topple_cells': [
                    (-1, 0), (1, 0), (0, -1), (0, 1),
                    (-2, 0), (2, 0), (0, -2), (0, 2),
                    ]
                },
            'o+': {
                'maxval': 12,
                'topple_cells': [
                    (-1, 0), (1, 0), (0, -1), (0, 1),
                    (-1, 1), (-1, -1), (1, 1), (1, -1),
                    (-1, 0), (1, 0), (0, -1), (0, 1)
                    ]
                },
            'ox': {
                'maxval': 12,
                'topple_cells': [
                    (-1, 0), (1, 0), (0, -1), (0, 1),
                    (-1, 1), (-1, -1), (1, 1), (1, -1),
                    (-1, 1), (-1, -1), (1, 1), (1, -1)
                    ]
                },
            'o++': {
                'maxval': 12,
                'topple_cells': [
                    (-1, 0), (1, 0), (0, -1), (0, 1),
                    (-1, 1), (-1, -1), (1, 1), (1, -1),
                    (-2, 0), (2, 0), (0, -2), (0, 2)
                    ]
                },
            'o-+': {
                'maxval': 16,
                'topple_cells': [
                    (-1, 0), (1, 0), (0, -1), (0, 1),
                    (-1, 0), (1, 0), (0, -1), (0, 1),
                    (-1, 1), (-1, -1), (1, 1), (1, -1),
                    (-2, 0), (2, 0), (0, -2), (0, 2)
                    ]
                },

            "Y": {
                'maxval': 16,
                'topple_cells': [
                    (0, 1), (0, -1), (1, 0), (-1, 0),
                    (0, 2), (0, -2), (2, 0), (-2, 0),
                    (2, 1), (2, -1), (-2, 1), (-2, -1),
                    (1, 2), (1, -2), (-1, 2), (-1, -2)
                    ]
            }
        }

    def __init__(self, sand_power=10, topple_pattern='+', for_animation=False):
        self.starting_sand = 2 ** sand_power

        if topple_pattern in self.patterns:
            self.topple_pattern = topple_pattern
            self.max_per_cell = self.patterns[topple_pattern]['maxval']
            self.topple_cells = self.patterns[topple_pattern]['topple_cells']
        else:
            err = 'Must use one of the following topple patterns: {}'
            raise ValueError(err.format(', '.join(self.patterns.keys())))

        self.init_grid(for_animation)
        self.for_animation = for_animation

    def init_grid(self, for_animation=False):
        side_length = int(self.starting_sand ** 0.5)
        if side_length % 2 == 0:
            side_length += 1

        if side_length < 10:
            # Lower order patterns end up with too small a side_length
            side_length = 10

        self.grid = np.zeros((side_length, side_length), np.int64)
        centre = int(side_length / 2)
        self.side_length = side_length
        self.centre = centre

        if not for_animation:
            self.grid[centre][centre] = self.starting_sand

        print("Grid initialised:\nside-length {}\ninitial sand {}".format(
            side_length, self.starting_sand
            )
        )

    def topple(self, verbose=False):
        '''Topple the sand in the grid until we reach a steady state'''
        start = time()
        passes = 0

        while np.max(self.grid) >= self.max_per_cell:
            for rowix, row in enumerate(self.grid):
                if np.max(row) >= self.max_per_cell:
                    for cellix, cell in enumerate(row):
                        if cell >= self.max_per_cell:
                            self.topple_cell(rowix, cellix)
            print(".", end="")
            passes += 1

        if verbose:
            t = time() - start
            print("\n{} passes required".format(passes))
            print("{}s to reach stable state".format(t))

        if not self.for_animation:
            self.trim_grid()

    def topple_cell(self, row, col):
        '''
        Distribute sand to neighbouring cells.
        Discards sand that falls off the grid
        '''
        n, rem = divmod(self.grid[row][col], self.max_per_cell)
        self.grid[row][col] = rem
        for trow, tcol in self.topple_cells:
            r, c = row + trow, col + tcol
            if ((0 <= r < self.side_length) and
                    (0 <= c < self.side_length)):
                self.grid[row + trow][col + tcol] += n

    def trim_grid(self, copy=False):
        grid = np.copy(self.grid) if copy else self.grid

        # Trim empty
        grid = [r for r in grid if sum(r) > 0]
        # Trim empty columns
        w1 = len(grid[0])
        trans = [[r[n] for r in grid] for n in range(w1)]
        trans = [r for r in trans if sum(r) > 0]
        w2 = len(trans[0])
        grid = [[r[n] for r in trans] for n in range(w2)]

        if copy:
            return grid
        else:
            self.grid = grid

    def print_grid(self):
        print(self.starting_sand)
        for row in self.grid:
            line = [str(cell) for cell in row]
            print(''.join(line))


def animate(n=50, k=10, step=1, pat='+', ftype='gif',
            fps=60, trim=True, cmap="RdYlBu"):
    '''Plot the first n steps of pattern k'''
    fig = plt.figure()
    s = SandHeap(k, pat)
    g = s.ntopple(step, verbose=True, trim=trim)
    ax = sns.heatmap(
            g, cbar=False, xticklabels=False,
            yticklabels=False, cmap=cmap
        )

    def init():
        ax = sns.heatmap(
                g, cbar=False, xticklabels=False,
                yticklabels=False, cmap=cmap
            )
        return ax,

    def animate(i, ax, fig):
        ax.cla()
        g = s.ntopple(step, True, trim=trim)
        ax = sns.heatmap(
                g, cbar=False, xticklabels=False,
                yticklabels=False, cmap=cmap, ax=ax
            )
        return ax,

    start = time()
    anim = animation.FuncAnimation(
            fig, animate, init_func=init, frames=n,
            fargs=(ax, fig), repeat_delay=50
        )

    if ftype == "mp4":
        fname = "2_{}_{}.mp4".format(k, pat)
        anim.save(fname, writer="ffmpeg", fps=fps, bitrate=2000)
    elif ftype == "gif":
        fname = "2_{}_{}.gif".format(k, pat)
        anim.save(fname, writer="imagemagick", fps=fps, dpi=100)
        # Trim border
        run(["convert", fname, "-fuzz", "1%", "-trim", "+repage", fname])
    plt.show()
    print(time() - start)
