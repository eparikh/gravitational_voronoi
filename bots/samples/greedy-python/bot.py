"""Greedy: tries a lattice of legal points and keeps the one that would own the most of a
coarse sample of the board, weight split evenly. A sample bot built from bots/templates/python."""
import json
import sys


class Bot:
    def start(self, msg):
        self.me = msg['you']
        self.k = msg['players']
        self.grid = msg['grid']
        self.min_dist = msg['min_dist']
        step = max(1, self.grid // 40)
        self.samples = [(x, y) for x in range(step // 2, self.grid, step)
                        for y in range(step // 2, self.grid, step)]

    def pulls(self, stones):
        """pull[p][i] at every sample point i, from the stones on the board."""
        pull = [[0.0] * len(self.samples) for _ in range(self.k)]
        for p, sx, sy, w in stones:
            row = pull[p - 1]
            for i, (x, y) in enumerate(self.samples):
                d2 = (x - sx) ** 2 + (y - sy) ** 2
                row[i] += w / d2 if d2 else 1e18
        return pull

    def move(self, msg):
        me = self.me - 1
        weight = msg['weight_left'][me] // msg['stones_left'][me]
        stones = msg['stones']
        if not stones:                     # an empty board: every point scores the same
            return self.grid // 2, self.grid // 2, weight
        md2 = self.min_dist ** 2
        pull = self.pulls(stones)
        mine = pull[me]
        rival = [max(v) if v else 0.0 for v in zip(*[pull[p] for p in range(self.k) if p != me])] \
            if self.k > 1 else [0.0] * len(self.samples)
        step = max(1, self.grid // 25)
        best, best_score = None, -1
        for cx in range(step // 2, self.grid, step):
            for cy in range(step // 2, self.grid, step):
                if any((cx - sx) ** 2 + (cy - sy) ** 2 < md2 for _, sx, sy, _ in stones):
                    continue
                score = 0
                for (x, y), m, r in zip(self.samples, mine, rival):
                    d2 = (x - cx) ** 2 + (y - cy) ** 2
                    if m + (weight / d2 if d2 else 1e18) > r:
                        score += 1
                if score > best_score:
                    best, best_score = (cx, cy), score
        if best is None:
            best = (0, 0)
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
