"""The rules: which stones are legal, and who owns every point.

The scoring is checked against a brute-force count in exact rational arithmetic on a small
board, for two players and for a melee, so the fast incremental update in the engine has
nothing to hide behind.
"""
import random
import unittest
from fractions import Fraction

from referee.engine import GRID, MIN_DIST, Game, load_config, make_config, whole


def brute_force(grid, stones, players):
    """Who owns every point, computed directly and exactly. owner[y][x] = seat or None."""
    at = {(s[1], s[2]): s[0] for s in stones}
    owner = [[None] * grid for _ in range(grid)]
    for y in range(grid):
        for x in range(grid):
            if (x, y) in at:
                owner[y][x] = at[(x, y)]
                continue
            pull = [Fraction(0)] * players
            for p, sx, sy, w in stones:
                pull[p] += Fraction(w, (x - sx) ** 2 + (y - sy) ** 2)
            best = max(pull)
            if best > 0 and pull.count(best) == 1:
                owner[y][x] = pull.index(best)
    return owner


def play_random(game, rng, tries=2000):
    """Fill a game with random legal stones (and random weights), as the referee would."""
    while not game.done():
        p = game.turn
        left = game.cfg.stones - game.placed[p] - game.skipped[p]
        w = rng.randint(1, game.weight_left[p] - (left - 1))
        for _ in range(tries):
            x, y = rng.randrange(game.grid), rng.randrange(game.grid)
            if game.check(p, {'x': x, 'y': y, 'weight': w})[1] is None:
                break
        stone, why = game.place(p, {'x': x, 'y': y, 'weight': w})
        game.advance()


class Scoring(unittest.TestCase):
    def check_against_brute_force(self, players, seed):
        rng = random.Random(seed)
        g = Game(make_config(4, 40), players=players, grid=48, min_dist=6)
        play_random(g, rng)
        stones = [(s['player'], s['x'], s['y'], s['weight']) for s in g.stones]
        exact = brute_force(g.grid, stones, players)
        for y in range(g.grid):
            for x in range(g.grid):
                self.assertEqual(g.owner_at(x, y), exact[y][x], f'point ({x}, {y}), seed {seed}')
        counts = [sum(row.count(p) for row in exact) for p in range(players)]
        self.assertEqual(g.scores(), counts)

    def test_two_players_match_exact_arithmetic(self):
        for seed in range(4):
            self.check_against_brute_force(2, seed)

    def test_a_melee_matches_exact_arithmetic(self):
        for seed in range(3):
            self.check_against_brute_force(4, 100 + seed)

    def test_the_first_stone_owns_the_whole_board(self):
        g = Game(make_config(2, 10), grid=30, min_dist=5)
        g.place(0, {'x': 3, 'y': 4, 'weight': 1})
        self.assertEqual(g.scores(), [30 * 30, 0])

    def test_equal_stones_tie_on_the_bisector(self):
        # Equal weights at (10, 15) and (20, 15): every point with x = 15 is a tie.
        g = Game(make_config(1, 5), grid=31, min_dist=5)
        g.place(0, {'x': 10, 'y': 15, 'weight': 5}); g.advance()
        g.place(1, {'x': 20, 'y': 15, 'weight': 5}); g.advance()
        self.assertTrue(all(g.owner_at(15, y) is None for y in range(31)))
        self.assertEqual(g.scores(), [15 * 31, 15 * 31])

    def test_a_stone_owns_its_own_point_even_when_outpulled(self):
        # A heavy red stone right next to a light blue one: blue still owns its own point.
        g = Game(make_config(1, 100), grid=40, min_dist=5)
        g.place(0, {'x': 10, 'y': 10, 'weight': 100}); g.advance()
        g.place(1, {'x': 15, 'y': 10, 'weight': 1}); g.advance()
        self.assertEqual(g.owner_at(15, 10), 1)
        self.assertEqual(g.owner_at(16, 10), 0)       # but red owns the point beside it

    def test_heavier_weight_takes_more_ground(self):
        g = Game(make_config(1, 9), grid=60, min_dist=10)
        g.place(0, {'x': 20, 'y': 30, 'weight': 9}); g.advance()
        g.place(1, {'x': 40, 'y': 30, 'weight': 1}); g.advance()
        self.assertGreater(g.scores()[0], g.scores()[1])


class Legality(unittest.TestCase):
    def setUp(self):
        self.g = Game(make_config(3, 10))
        self.g.place(0, {'x': 500, 'y': 500, 'weight': 2})
        self.g.advance()

    def refused(self, reply, player=1):
        stone, why = self.g.check(player, reply)
        return why

    def test_the_real_board_and_distance(self):
        self.assertEqual((self.g.grid, self.g.min_dist), (GRID, MIN_DIST))
        self.assertEqual((GRID, MIN_DIST), (1000, 66))

    def test_exactly_min_dist_is_allowed_and_closer_is_not(self):
        self.assertIsNone(self.refused({'x': 566, 'y': 500, 'weight': 1}))
        self.assertIn('at least 66 apart', self.refused({'x': 565, 'y': 500, 'weight': 1}))
        # 3-4-5 style: (540, 552) is sqrt(40^2 + 52^2) = 65.6 away
        self.assertIsNotNone(self.refused({'x': 540, 'y': 552, 'weight': 1}))

    def test_distance_applies_to_your_own_stones_too(self):
        self.assertIn('its own', self.refused({'x': 510, 'y': 500, 'weight': 1}, player=0))

    def test_off_the_board(self):
        for x, y in ((1000, 5), (-1, 5), (5, 1000), (5, -3)):
            self.assertIn('off the board', self.refused({'x': x, 'y': y, 'weight': 1}))

    def test_weights_must_be_positive_whole_and_affordable(self):
        self.assertIn('at least 1', self.refused({'x': 100, 'y': 100, 'weight': 0}))
        self.assertIn('at least 1', self.refused({'x': 100, 'y': 100, 'weight': -50}))
        self.assertIn('not a whole number', self.refused({'x': 100, 'y': 100, 'weight': 2.5}))
        self.assertIn('more than the 10 left', self.refused({'x': 100, 'y': 100, 'weight': 11}))
        self.assertIsNone(self.refused({'x': 100, 'y': 100, 'weight': 10}))

    def test_numbers_written_as_floats_or_strings_are_read(self):
        self.assertIsNone(self.refused({'x': 100.0, 'y': '100', 'weight': '3'}))
        self.assertIn('not a whole number', self.refused({'x': 100.5, 'y': 100, 'weight': 1}))
        self.assertIn('not a whole number', self.refused({'x': True, 'y': 100, 'weight': 1}))
        self.assertIn('no "weight"', self.refused({'x': 100, 'y': 100}))

    def test_a_refused_stone_is_a_skipped_turn(self):
        stone, why = self.g.place(1, {'x': 1, 'y': 1, 'weight': 99})
        self.assertIsNone(stone)
        self.assertEqual(self.g.skipped, [0, 1])
        self.assertEqual(self.g.weight_left, [8, 10])       # nothing was spent
        self.g.advance()
        self.assertEqual(self.g.state()['stones_left'], [2, 2])

    def test_the_game_lasts_players_times_stones_turns_and_the_last_seat_ends_it(self):
        g = Game(make_config(2, 4), players=3, grid=50, min_dist=5)
        seats = []
        while not g.done():
            seats.append(g.turn)
            g.skip(g.turn)
            g.advance()
        self.assertEqual(seats, [0, 1, 2, 0, 1, 2])


class Parameters(unittest.TestCase):
    def test_parameter_checks(self):
        self.assertEqual(make_config(10, 100).as_dict(), {'stones': 10, 'weight': 100})
        self.assertRaises(ValueError, make_config, 0, 10)
        self.assertRaises(ValueError, make_config, 10, 9)        # 10 stones need weight >= 10
        self.assertRaises(ValueError, make_config, 'ten', 100)
        self.assertIsNotNone(make_config(200, 1000).warning)

    def test_the_shipped_parameter_files_load(self):
        from referee.runner import ROOT
        for f in (ROOT / 'params').glob('*.txt'):
            load_config(f)

    def test_whole(self):
        self.assertEqual([whole(v) for v in (3, 3.0, '3', ' 3 ', '3.0')], [3, 3, 3, 3, 3])
        self.assertEqual([whole(v) for v in (3.5, 'x', None, [], True)], [None] * 5)


if __name__ == '__main__':
    unittest.main()
