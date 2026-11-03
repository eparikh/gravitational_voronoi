"""A Gravitational Voronoi bot in Python 3. Copy this folder to bots/<your-name>/ and write
your strategy in the section marked EDIT ONLY THIS SECTION.

The referee runs this file as a subprocess: one JSON message per line arrives on standard
input, one JSON object per line goes back on standard output. Print anything you like to
standard error (print(..., file=sys.stderr)) for debugging; the referee ignores it. A stray
print() to standard output breaks the protocol and forfeits your game.

The board is grid x grid integer points: x from 0 (left) to grid-1, y from 0 (top) to grid-1.

Messages you receive:
  {"type": "start", "you": 1, "players": 2, "color": "red", "grid": 1000, "min_dist": 66,
   "stones": 10, "weight": 100, "clock": 120}
      -> reply {"ready": true}.  This one is not on your clock.
  {"type": "move", ...the whole position, see below...}
      -> reply {"x": 500, "y": 500, "weight": 10}

A move message carries everything, so a bot never has to remember anything:

  you, players, color      your seat (1 moves first), how many players, your colour
  grid, min_dist           board size, and the minimum distance between any two stones
  stones_each, weight_each the parameters of this game
  turn                     which of your stones this is (1 .. stones_each)
  stones                   every stone so far, in order: [player, x, y, weight]
  stones_left              turns each player has left (index 0 = player 1)
  weight_left              weight each player has left
  scores                   points each player owns right now
  clock                    your thinking time left, in seconds

Rules the referee enforces. x, y and weight are whole numbers. The stone must be on the
board, at least min_dist from every stone already placed (yours too), and its weight must
be at least 1 and no more than your weight left. Keep at least 1 weight for each stone you
still have to place. An illegal stone is not placed and that turn is skipped.

You have "clock" seconds of thinking time for the whole game, counted only while the referee
waits for your answer. Run out and you forfeit the rest of the game.
"""
import json
import random
import sys


# ----------------------------------------------------------------------------
# EDIT ONLY THIS SECTION
# ----------------------------------------------------------------------------

class Bot:
    def start(self, msg):
        """Called once, before the game. Keep whatever you need from msg."""
        self.me = msg['you']
        self.grid = msg['grid']
        self.min_dist = msg['min_dist']

    def move(self, msg):
        """Return (x, y, weight) for your next stone."""
        me = self.me - 1
        stones_left = msg['stones_left'][me]
        weight = msg['weight_left'][me] // stones_left        # split the weight evenly
        for _ in range(10000):
            x, y = random.randrange(self.grid), random.randrange(self.grid)
            if all((x - sx) ** 2 + (y - sy) ** 2 >= self.min_dist ** 2
                   for _, sx, sy, _ in msg['stones']):
                return x, y, weight
        return 0, 0, weight


# ----------------------------------------------------------------------------
# Below here is the plumbing. You should not need to change it.
# ----------------------------------------------------------------------------

def main():
    bot = Bot()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        kind = msg.get('type')
        if kind == 'start':
            bot.start(msg)
            reply = {'ready': True}
        elif kind == 'move':
            x, y, w = bot.move(msg)
            reply = {'x': x, 'y': y, 'weight': w}
        else:
            reply = {}
        sys.stdout.write(json.dumps(reply) + '\n')
        sys.stdout.flush()


if __name__ == '__main__':
    main()
