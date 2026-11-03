"""Spread: puts each stone as far as it can from every stone already on the board, with the
weight split evenly. A sample bot built from bots/templates/python."""
import json
import sys


class Bot:
    def start(self, msg):
        self.me = msg['you']
        self.grid = msg['grid']
        self.min_dist = msg['min_dist']

    def move(self, msg):
        me = self.me - 1
        weight = msg['weight_left'][me] // msg['stones_left'][me]
        stones = msg['stones']
        if not stones:
            c = self.grid // 2
            return c, c, weight
        best, best_d = (0, 0), -1
        step = max(1, self.grid // 50)
        for x in range(step // 2, self.grid, step):
            for y in range(step // 2, self.grid, step):
                d = min((x - sx) ** 2 + (y - sy) ** 2 for _, sx, sy, _ in stones)
                if d > best_d:
                    best, best_d = (x, y), d
        return best[0], best[1], weight


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
