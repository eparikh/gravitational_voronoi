# A Gravitational Voronoi bot in Julia. Copy this folder to bots/<your-name>/ and write your
# strategy in the section marked EDIT ONLY THIS SECTION.
#
# The referee runs this program as a subprocess: one JSON message per line arrives on standard
# input, one JSON object per line goes back on standard output. Print to standard error
# (println(stderr, ...)) for debugging; the referee ignores it.
#
# The board is grid x grid integer points: x from 0 (left), y from 0 (top). These are 0-based,
# like the rest of the architecture. Player numbers ("you", and the first entry of each stone)
# are 1-based, so they index Julia arrays such as weight_left directly.
#
# Messages you receive:
#   {"type":"start","you":1,"players":2,"color":"red","grid":1000,"min_dist":66,
#    "stones":10,"weight":100,"clock":120}
#       -> reply {"ready":true}.  This one is not on your clock.
#   {"type":"move", ...}  -> reply {"x":500,"y":500,"weight":10}
#
# A move message carries the whole position: "stones" (every stone so far, as
# [player,x,y,weight]), "stones_left" and "weight_left" (one number per player), "scores",
# "turn" and "clock". See the main README for every field.

# -- the smallest amount of JSON reading this bot needs -----------------------

"The integer that follows \"key\": in the message, or fallback when it is not there."
function field(line::String, key::String, fallback::Int=-1)
    m = match(Regex("\"" * key * "\":(-?\\d+)"), line)
    m === nothing ? fallback : parse(Int, m.captures[1])
end

"""The list of integers that follows \"key\": [ ... ]. For the flat lists: `stones_left`,
`weight_left`, `scores`. `stones` is a list OF lists, so read it with `list_of_lists`."""
function list_field(line::String, key::String)
    m = match(Regex("\"" * key * "\":\\[([^\\[\\]]*)\\]"), line)
    m === nothing && return Int[]
    body = strip(m.captures[1])
    isempty(body) && return Int[]
    [parse(Int, strip(x)) for x in split(body, ',') if !isempty(strip(x))]
end

"The list of lists that follows \"key\": [[...],[...]], used for stones."
function list_of_lists(line::String, key::String)
    at = findfirst("\"" * key * "\":[", line)
    at === nothing && return Vector{Int}[]
    out = Vector{Int}[]
    depth = 0
    buf = IOBuffer()
    for ch in line[(last(at)):end]
        if ch == '['
            depth += 1
            depth == 2 && (buf = IOBuffer())
        elseif ch == ']'
            if depth == 2
                body = strip(String(take!(buf)))
                push!(out, isempty(body) ? Int[] :
                      [parse(Int, strip(x)) for x in split(body, ',') if !isempty(strip(x))])
            end
            depth -= 1
            depth == 0 && break
        elseif depth == 2
            write(buf, ch)
        end
    end
    out
end

has_type(line, what) = occursin("\"type\":\"$what\"", line)

# -----------------------------------------------------------------------------
# EDIT ONLY THIS SECTION
# -----------------------------------------------------------------------------

mutable struct Bot
    me::Int
    grid::Int
    min_dist::Int
    Bot() = new(1, 1000, 66)
end

function start!(bot::Bot, line::String)
    bot.me = field(line, "you", 1)
    bot.grid = field(line, "grid", 1000)
    bot.min_dist = field(line, "min_dist", 66)
end

"Return (x, y, weight) for your next stone: a random legal point, weight split evenly."
function move(bot::Bot, line::String)
    stones = list_of_lists(line, "stones")        # each is [player, x, y, weight]
    left = max(1, list_field(line, "stones_left")[bot.me])
    weight = list_field(line, "weight_left")[bot.me] ÷ left
    md2 = bot.min_dist^2
    for _ in 1:10000
        x, y = rand(0:bot.grid-1), rand(0:bot.grid-1)
        if all((x - s[2])^2 + (y - s[3])^2 >= md2 for s in stones)
            return x, y, weight
        end
    end
    return 0, 0, weight
end

# -----------------------------------------------------------------------------
# Below here is the plumbing. You should not need to change it.
# -----------------------------------------------------------------------------

function main()
    bot = Bot()
    for line in eachline(stdin)
        isempty(strip(line)) && continue
        if has_type(line, "start")
            start!(bot, line)
            println("{\"ready\":true}")
        elseif has_type(line, "move")
            x, y, w = move(bot, line)
            println("{\"x\":", x, ",\"y\":", y, ",\"weight\":", w, "}")
        else
            println("{}")
        end
        flush(stdout)
    end
end

main()
