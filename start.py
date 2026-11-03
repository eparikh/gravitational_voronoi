"""Gravitational Voronoi:  python3 start.py [command] [options]

  python3 start.py                               start the dashboard (http://127.0.0.1:8093)
  python3 start.py match "Bot 1" "Bot 2"         play one match (each bot moves first once)
  python3 start.py match "A" "B" "C"             a melee: one game per bot, seats rotating
  python3 start.py tournament                    every pair of bots, no browser
  python3 start.py tournament --melee            one melee with every bot, no browser
  python3 start.py params --stones 10 --weight 100 --out params/my_game.txt
  python3 start.py verify results/match/results.json   check a finished match against every rule

Add --help after a command to see its options.
"""
import sys

if sys.version_info < (3, 8):
    sys.exit('Gravitational Voronoi needs Python 3.8 or newer.')

from referee import make_params, match, server, tournament, verify  # noqa: E402

COMMANDS = {'serve': server.main, 'match': match.main, 'tournament': tournament.main,
            'params': make_params.main, 'verify': verify.main}


def main():
    args = sys.argv[1:]
    if args and args[0] in ('-h', '--help', 'help'):
        print(__doc__)
        return
    name = args[0] if args and args[0] in COMMANDS else 'serve'
    if args and args[0] in COMMANDS:
        args = args[1:]
    sys.argv = [f'python3 start.py {name}'] + args
    try:
        COMMANDS[name]()
    except KeyboardInterrupt:
        print('\nStopped.')
    except (OSError, ValueError) as exc:
        sys.exit(f'Error: {exc}')


if __name__ == '__main__':
    main()
