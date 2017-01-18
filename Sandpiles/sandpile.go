package main

import (
	"fmt"
	"math"
	"os"
	"strconv"
	"strings"
	"time"
)

type gridRef struct {
	x, y int
}

// Control class for coordinating topples and collecting results
type grid struct {
	startingSand    int
	maxBeforeTopple int
	topplePattern   string
	offsets         []gridRef
	cells           [][]int
}

// Neighbouring cell offsets for toppling
var neighbourOffsets = map[string][]gridRef{
	"+": []gridRef{{0, 1}, {0, -1}, {1, 0}, {-1, 0}},
	"x": []gridRef{{1, 1}, {1, -1}, {-1, 1}, {-1, -1}},
	"o": []gridRef{
		{0, 1}, {0, -1}, {1, 0}, {-1, 0},
		{1, 1}, {1, -1}, {-1, 1}, {-1, -1},
	},
	"o+": []gridRef{
		{0, 1}, {0, -1}, {1, 0}, {-1, 0},
		{0, 1}, {0, -1}, {1, 0}, {-1, 0},
		{1, 1}, {1, -1}, {-1, 1}, {-1, -1},
	},
	"ox": []gridRef{
		{0, 1}, {0, -1}, {1, 0}, {-1, 0},
		{1, 1}, {1, -1}, {-1, 1}, {-1, -1},
		{1, 1}, {1, -1}, {-1, 1}, {-1, -1},
	},
}

// Join an array of ints as a deliminated string
func arrayToString(a []int, delim string, newline bool) string {
	s := strings.Trim(strings.Replace(fmt.Sprint(a), " ", delim, -1), "[]")
	if newline == true {
		return strings.Join([]string{s, "\n"}, "")
	} else {
		return s
	}
}

// Create a new grid and start the origin cell toppling
func initialiseGrid(sandPower int, pattern string) *grid {
	sand := int(math.Pow(2.0, float64(sandPower)))
	sideLength := int(math.Sqrt(float64(sand))) + 1
	if sideLength%2 == 0 {
		sideLength += 1
	}
	centre := int(sideLength / 2)

	cells := make([][]int, sideLength)
	for i := 0; int(i) < sideLength; i++ {
		cells[i] = make([]int, sideLength)
	}
	cells[centre][centre] = sand

	g := grid{
		startingSand:    sand,
		topplePattern:   pattern,
		offsets:         neighbourOffsets[pattern],
		maxBeforeTopple: int(len(neighbourOffsets[pattern])),
		cells:           cells,
	}

	return &g
}

// Topple each cell until everything stabilises
func (g *grid) topple() {
	for g.max() >= g.maxBeforeTopple {
		for i, row := range g.cells {
			for j, col := range row {
				if col >= g.maxBeforeTopple {
					g.toppleCell(int(i), int(j))
				}
			}
		}
	}
}

// Send sand to neighbouring cells
func (g *grid) toppleCell(i, j int) {
	sand := g.cells[i][j]
	remaining := sand % g.maxBeforeTopple
	toppleSand := (sand - remaining) / g.maxBeforeTopple
	g.cells[i][j] = remaining
	for _, o := range g.offsets {
		g.cells[i+o.x][j+o.y] += toppleSand
	}
}

// Find the max value of in the grid
func (g *grid) max() int {
	m := int(0)
	for _, row := range g.cells {
		for _, col := range row {
			if col > m {
				m = col
			}
		}
	}
	return m
}

// Print the grid
func (g *grid) visualise(sandPower string, print bool) {
	s := []string{"2_", sandPower, "_", g.topplePattern, ".csv"}
	fname := strings.Join(s, "")
	f, err := os.Create(fname)
	if err != nil {
		panic("error creating file")
	}
	defer f.Close()

	for _, row := range g.cells {
		_, err := f.WriteString(arrayToString(row, ",", true))
		if print == true {
			fmt.Println(arrayToString(row, "", false))
		}
		if err != nil {
			panic("error in writing")
		}
	}
	f.Sync()
}

// Start a cascade and collect in the results
func main() {
	args := os.Args[1:]
	sandPower, err := strconv.Atoi(args[0])
	if err != nil {
		fmt.Println(err)
		os.Exit(-1)
	}
	pattern := args[1]
	sandHeap := initialiseGrid(int(sandPower), pattern)
	fmt.Printf("Starting sand: %v\nPattern: %v\nSide length: %v\n",
		sandHeap.startingSand, sandHeap.topplePattern, len(sandHeap.cells))
	start := time.Now()
	sandHeap.topple()
	end := time.Since(start)
	sandHeap.visualise(args[0], false)
	fmt.Println(end)
}
