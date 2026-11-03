"""Random: a random legal point, weight split evenly. This is the Python template unchanged,
kept as a sample opponent (a punching bag)."""
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
