'''
Sandpile dynamical system simulation
------------------------------------
TODO::  Have the grid grow dynamically / allocate
        the _correct_ size of grid rather than over
        allocating and then trimming to size.

Seaborn plotting:
> plt.figure(figsize=(15, 15))
> sns.heatmap(s.grid, cbar=False, xticklabels=False,
>             yticklabels=False, cmap="RdYlBu")
'''
# %pylab inline
# import seaborn as sns
from time import time


class SandHeap:
    '''Control class for managaing sandpile topples'''
    patterns = {
        '+': {
            'maxval': 4,
            'topple_cells': [(-1, 0), (1, 0), (0, -1), (0, 1)]
            },
        'x': {
            'maxval': 4,
            'topple_cells': [(-1, 1), (-1, -1), (-1, 1), (-1, -1)]
            },
        'o': {
            'maxval': 8,
            'topple_cells': [
                (-1, 0), (1, 0), (0, -1), (0, 1),
                (-1, 1), (-1, -1), (1, 1), (1, -1)
                ]
            }
        }

    def __init__(self, sand_power=10, topple_pattern='+', init=[[1, 0, 1]]):
        '''
        + is the standard sandpile pattern: others may be more interesting!
        '''
        self.starting_sand = 2 ** sand_power
        self.topple_pattern = topple_pattern
        self.max_per_cell = self.patterns[topple_pattern]['maxval']
        self.topple_cells = self.patterns[topple_pattern]['topple_cells']
        self.init_grid(init)

    def init_grid(self, init):
        '''
        Construct a grid large enough for the sand specified.
        Different configurations may be interesting to check out.
        '''
        # TODO:: allow for different starting distributions to be specified
        side_length = int(self.starting_sand ** 0.5) + 1
        centre = int(side_length / 2)
        grid = [[0 for j in range(side_length)] for k in range(side_length)]
        grid[centre][centre] = self.starting_sand
        self.grid = grid

    def topple(self):
        '''
        Topple the sand in the grid until we reach a steady state
        '''
        start = time()
        while max([max(r) for r in self.grid]) >= self.max_per_cell:
            for rowix, row in enumerate(self.grid):
                for cellix, cell in enumerate(row):
                    if cell >= self.max_per_cell:
                        self.topple_cell(rowix, cellix)
        print(time() - start)
        self.trim_grid()
        self.print_grid()

    def topple_cell(self, row, col):
        '''
        Distribute sand to neighbouring cells according to the pattern
        specified at initialisation.
        '''
        while self.grid[row][col] >= self.max_per_cell:
            self.grid[row][col] -= self.max_per_cell
            for trow, tcol in self.topple_cells:
                self.grid[row + trow][col + tcol] += 1

    def trim_grid(self):
        '''
        Remove 0 filled edge rows/columns for a nicer visualisation
        '''
        # Trim empty rows
        self.grid = [r for r in self.grid if sum(r) > 0]
        # Trim empty columns
        w1 = len(self.grid[0])
        trans = [[r[n] for r in self.grid] for n in range(w1)]
        trans = [r for r in trans if sum(r) > 0]
        w2 = len(trans[0])
        self.grid = [[r[n] for r in trans] for n in range(w2)]

    def print_grid(self):
        '''
        Pretty print the grid after a run
        '''
        for row in self.grid:
            print(''.join([str(cell) for cell in row]))
