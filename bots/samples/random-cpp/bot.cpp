// A Gravitational Voronoi bot in C++. Copy this folder to bots/<your-name>/ and write your
// strategy in the section marked EDIT ONLY THIS SECTION.
//
// The referee compiles it (build.py) before any clock starts, then runs ./bot as a
// subprocess: one JSON message per line arrives on standard input, one JSON object per line
// goes back on standard output. Print anything you like to standard error (std::cerr) for
// debugging; the referee ignores it. Flush after every reply.
//
// The board is grid x grid integer points: x from 0 (left), y from 0 (top).
//
// Messages you receive:
//   {"type":"start","you":1,"players":2,"color":"red","grid":1000,"min_dist":66,
//    "stones":10,"weight":100,"clock":120}
//       -> reply {"ready":true}.  This one is not on your clock.
//   {"type":"move", ...}  -> reply {"x":500,"y":500,"weight":10}
//
// A move message carries the whole position: "stones" (every stone so far, as
// [player,x,y,weight]), "stones_left" and "weight_left" (one number per player, index 0 is
// player 1), "scores", "turn" and "clock". See the main README for every field.
//
// A stone must be on the board, at least min_dist from every stone already placed, and its
// weight a whole number from 1 to your weight left. An illegal stone is not placed and that
// turn is skipped.

#include <cctype>
#include <cstdlib>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// -- the smallest amount of JSON reading this bot needs ----------------------

// The integer that follows "key": in the message, or fallback when it is not there.
static long long field(const std::string& line, const std::string& key, long long fallback = -1) {
    auto at = line.find("\"" + key + "\":");
    if (at == std::string::npos) return fallback;
    return std::strtoll(line.c_str() + at + key.size() + 3, nullptr, 10);
}

// The list of integers that follows "key": [ ... ]. For the flat lists: stones_left,
// weight_left, scores. "stones" is a list of lists, so read it with list_of_lists.
static std::vector<long long> list_field(const std::string& line, const std::string& key) {
    std::vector<long long> out;
    auto at = line.find("\"" + key + "\":[");
    if (at == std::string::npos) return out;
    auto end = line.find(']', at);
    const char* p = line.c_str() + at + key.size() + 4;
    const char* stop = line.c_str() + end;
    while (p < stop) {
        char* next;
        long long v = std::strtoll(p, &next, 10);
        if (next == p) { ++p; continue; }
        out.push_back(v);
        p = next;
    }
    return out;
}

// The list of lists that follows "key": [[...],[...]], used for "stones".
static std::vector<std::vector<long long>> list_of_lists(const std::string& line, const std::string& key) {
    std::vector<std::vector<long long>> out;
    auto at = line.find("\"" + key + "\":[");
    if (at == std::string::npos) return out;
    int depth = 0;
    std::vector<long long> cur;
    for (size_t i = at + key.size() + 3; i < line.size(); ++i) {
        char ch = line[i];
        if (ch == '[') {
            if (++depth == 2) cur.clear();
        } else if (ch == ']') {
            if (depth == 2) out.push_back(cur);
            if (--depth == 0) break;
        } else if (depth == 2 && (std::isdigit(static_cast<unsigned char>(ch)) || ch == '-')) {
            char* next;
            cur.push_back(std::strtoll(line.c_str() + i, &next, 10));
            i = static_cast<size_t>(next - line.c_str()) - 1;
        }
    }
    return out;
}

static bool has_type(const std::string& line, const char* what) {
    return line.find(std::string("\"type\":\"") + what + "\"") != std::string::npos;
}

// ----------------------------------------------------------------------------
// EDIT ONLY THIS SECTION
// ----------------------------------------------------------------------------

struct Move { long long x, y, weight; };

struct Bot {
    int me = 1, grid = 1000, min_dist = 66;
    std::mt19937 rng{std::random_device{}()};

    void start(const std::string& line) {
        me = static_cast<int>(field(line, "you", 1));
        grid = static_cast<int>(field(line, "grid", 1000));
        min_dist = static_cast<int>(field(line, "min_dist", 66));
    }

    // Return your next stone: a random legal point, with the weight split evenly.
    Move move(const std::string& line) {
        auto stones = list_of_lists(line, "stones");         // each is {player, x, y, weight}
        auto stones_left = list_field(line, "stones_left");
        auto weight_left = list_field(line, "weight_left");
        long long left = stones_left.at(me - 1) > 0 ? stones_left.at(me - 1) : 1;
        long long weight = weight_left.at(me - 1) / left;
        std::uniform_int_distribution<int> pick(0, grid - 1);
        long long md2 = 1LL * min_dist * min_dist;
        for (int tries = 0; tries < 10000; ++tries) {
            long long x = pick(rng), y = pick(rng);
            bool ok = true;
            for (const auto& s : stones) {
                long long dx = x - s[1], dy = y - s[2];
                if (dx * dx + dy * dy < md2) { ok = false; break; }
            }
            if (ok) return {x, y, weight};
        }
        return {0, 0, weight};
    }
};

// ----------------------------------------------------------------------------
// Below here is the plumbing. You should not need to change it.
// ----------------------------------------------------------------------------

int main() {
    std::ios::sync_with_stdio(false);
    Bot bot;
    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        if (has_type(line, "start")) {
            bot.start(line);
            std::cout << "{\"ready\":true}\n" << std::flush;
        } else if (has_type(line, "move")) {
            Move m = bot.move(line);
            std::cout << "{\"x\":" << m.x << ",\"y\":" << m.y << ",\"weight\":" << m.weight
                      << "}\n" << std::flush;
        } else {
            std::cout << "{}\n" << std::flush;
        }
    }
    return 0;
}
