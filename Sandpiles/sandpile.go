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
	// Simple Symmetric
	"+": []gridRef{{0, 1}, {0, -1}, {1, 0}, {-1, 0}},
	"x": []gridRef{{1, 1}, {1, -1}, {-1, 1}, {-1, -1}},
	"o": []gridRef{
		{0, 1}, {0, -1}, {1, 0}, {-1, 0},
		{1, 1}, {1, -1}, {-1, 1}, {-1, -1},
	},
	// asymmetrical {should only be used for seeding}
	"\\": []gridRef{{1, -1}, {-1, 1}},
	"/":  []gridRef{{1, 1}, {-1, -1}},
	"|":  []gridRef{{1, 0}, {-1, 0}},
	"-":  []gridRef{{0, 1}, {0, -1}},
	// compound
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
	"++": []gridRef{
		{0, 1}, {0, -1}, {1, 0}, {-1, 0},
		{0, 2}, {0, -2}, {2, 0}, {-2, 0},
	},
	"o++": []gridRef{
		{0, 1}, {0, -1}, {1, 0}, {-1, 0},
		{0, 2}, {0, -2}, {2, 0}, {-2, 0},
		{1, 1}, {1, -1}, {-1, 1}, {-1, -1},
	},
	// "fat" version of the above {not as nice}
	"o-+": []gridRef{
		{0, 1}, {0, -1}, {1, 0}, {-1, 0},
		{0, 1}, {0, -1}, {1, 0}, {-1, 0},
		{0, 2}, {0, -2}, {2, 0}, {-2, 0},
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
func initialiseGrid(sandPower int, pattern, startOnPattern string) *grid {
	sand := int(math.Pow(2.0, float64(sandPower)))
	sideLength := int(math.Sqrt(float64(sand))) + 1
	if pattern == "x" {
		sideLength = int(float64(sideLength) * 1.5)
	}
	if sideLength%2 == 0 {
		sideLength += 1
	}
	centre := int(sideLength / 2)

	cells := make([][]int, sideLength)
	for i := 0; int(i) < sideLength; i++ {
		cells[i] = make([]int, sideLength)
	}
	if startOnPattern != "." {
		for _, o := range neighbourOffsets[startOnPattern] {
			perCell := len(neighbourOffsets[startOnPattern])
			cells[centre+o.x][centre+o.y] = sand / perCell
		}
	} else {
		cells[centre][centre] = sand
	}

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
	passes := 0
	for {
		toppled := false
		for i, row := range g.cells {
			for j, col := range row {
				if col >= g.maxBeforeTopple {
					sand := g.cells[i][j]
					remaining := sand % g.maxBeforeTopple
					toppleSand := (sand - remaining) / g.maxBeforeTopple
					g.cells[i][j] = remaining
					for _, o := range g.offsets {
						g.cells[i+o.x][j+o.y] += toppleSand
					}
					toppled = true
				}
			}
		}
		passes += 1
		if passes%10 == 0 {
			fmt.Print(".")
		}
		if toppled == false {
			// We've reached steady state
			break
		}
	}
	fmt.Println()
	fmt.Printf("%v passes to complete\n", passes)
}

// Print the grid
func (g *grid) visualise(sandPower, seed string, print bool) {
	var s []string
	if seed == "." {
		s = []string{"csv/2_", sandPower, "_", g.topplePattern, ".csv"}
	} else {
		s = []string{"csv/2_", sandPower, "_", g.topplePattern, "_", seed, ".csv"}
	}
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
	sandHeap := initialiseGrid(int(sandPower), pattern, args[2])
	fmt.Printf("Starting sand: %v\nPattern: %v\nSide length: %v\n",
		sandHeap.startingSand, sandHeap.topplePattern, len(sandHeap.cells))
	start := time.Now()
	sandHeap.topple()
	end := time.Since(start)
	sandHeap.visualise(args[0], args[2], false)
	fmt.Println(end)
}