"""Write a parameter file: the stones per player and the total weight per player.

  python3 start.py params --stones 10 --weight 100 --out params/my_game.txt
"""
import argparse

from .engine import make_config
from .runner import ROOT


def write_params(path, cfg):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'# stones per player, total weight per player\n'
                    f'{cfg.stones}\n{cfg.weight}\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--stones', type=int, required=True, help='stones per player')
    ap.add_argument('--weight', type=int, required=True, help='total weight per player')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    cfg = make_config(args.stones, args.weight)
    write_params(ROOT / args.out, cfg)
    if cfg.warning:
        print(f'Note: {cfg.warning}')
    print(f'Wrote {args.out}: {cfg}')


if __name__ == '__main__':
    main()
