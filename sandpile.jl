using Gadfly

const C = [
    Colors.RGB(a/255,b/255,c/255)
    for (a,b,c) in [(117,107,177), (117,107,177), (49,130,189)]
]

const PALETTE = Scale.color_discrete_manual(C...)

const patterns = Dict(
    "+" => Dict(
        "maxval" => 4,
        "toppleCells" => [(-1, 0), (1, 0), (0, -1), (0, 1)]
        ),
    "x" => Dict(
        "maxval" => 4,
        "toppleCells" => [(-1, 1), (-1, -1), (-1, 1), (-1, -1)]
        ),
    "o" => Dict(
        "maxval" => 8,
        "toppleCells" => [(0, 1), (1, 0), (0, -1), (-1, 0),
                          (1, 1), (1, -1), (-1, 1), (-1, -1)]
        )
)

type SandPile
    startingSand::Int64
    topplePattern::String
    maxPerCell::Int64
    sideLength::Int64
    toppleCells::Array{Tuple{Int8,Int8}}
    grid::Array{Array{Int64}}

    function SandPile(sandPower::Int, pattern::String)
        startingSand = 2 ^ sandPower
        maxPerCell = patterns[pattern]["maxval"]
        toppleCells = patterns[pattern]["toppleCells"]
        sideLength = Int(round(sqrt(startingSand))) + 1

        if sideLength % 2 == 0
            sideLength += 1
        end

        centre = Int(round(sideLength / 2)) + 1
        grid = [[0 for i in 1:sideLength] for j in 1:sideLength]
        grid[centre][centre] = startingSand

        new(startingSand, pattern, maxPerCell, sideLength, toppleCells, grid)
    end
end

lmax(a::Array{Array{Int}}) = maximum([maximum(r) for r in a])

function topple!(s::SandPile; verbose=true)
    n = 1

    while lmax(s.grid) >= s.maxPerCell
        for (rowix, row) in enumerate(s.grid)
            for (colix, col) in enumerate(row)
                col >= s.maxPerCell && toppleCell!(s, rowix, colix)
            end
        end
        n += 1
    end
    verbose && println(n)
    trimGrid!(s)
end

function toppleCell!(s::SandPile, row::Int, col::Int)
    while s.grid[row][col] >= s.maxPerCell
        s.grid[row][col] -= s.maxPerCell
        for (trow, tcol) in s.toppleCells
            s.grid[row+trow][col+tcol] += 1
        end
    end
end

function trimGrid!(s::SandPile)
    # Trim rows
    g = [r for r in s.grid if sum(r) > 0]
    h = transpose(hcat(g...))
    r, c = size(h)
    t = [h[:,n] for n in 1:c]
    g = [r for r in t if sum(r) > 0]
    s.grid = g
end

function vis(s; dims=(2000,2000), filename="")
    plot_style = style(
        background_color=colorant"white",
        minor_label_color=colorant"white",
        minor_label_font_size=1px,
        key_position=:none
    )
    Gadfly.push_theme(plot_style)
    plt = spy(
            hcat(s.grid...),
            Guide.title(""),
            Guide.xlabel(nothing),
            Guide.ylabel(nothing),
            PALETTE
        )

    if filename != ""
        x, y = dims
        if endswith(filename, ".png")
            img = PNG(filename, x*px, y*px)
            draw(img, plt)
        else
            error("filename must end in .png")
        end
    else
        return plt
    end
end
