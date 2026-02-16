#!/usr/bin/env python3
import json
import urllib.parse
import datetime
from pathlib import Path
import argparse

ALIASES = {
    'player': 'Маша',
    'masha': 'Маша',
    'Маша': 'Маша',
    'Stas': 'Стас',
    'stas': 'Стас',
    'Стас': 'Стас',
}


def canon_name(name: str) -> str:
    n = urllib.parse.unquote(name or 'player').strip()
    return ALIASES.get(n, ALIASES.get(n.lower(), n))


def compute_tables(scores):
    best = {}
    total = {}
    for e in scores:
        n = e['name']
        s = int(e['score'])
        best[n] = max(best.get(n, 0), s)
        total[n] = total.get(n, 0) + s

    best_table = sorted(best.items(), key=lambda kv: (-kv[1], kv[0]))
    total_table = sorted(total.items(), key=lambda kv: (-kv[1], kv[0]))
    return best_table, total_table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='.')
    ap.add_argument('--submit', required=True, help='score_submit|game=pong10|name=...|score=..|ts=..')
    ap.add_argument('--user', default='unknown')
    args = ap.parse_args()

    path = Path(args.repo) / 'leaderboard.json'
    if path.exists():
        data = json.loads(path.read_text(encoding='utf-8'))
    else:
        data = {'game': 'pong10', 'updatedAt': None, 'scores': []}

    parts = args.submit.split('|')
    kv = {}
    for p in parts[1:]:
        if '=' in p:
            k, v = p.split('=', 1)
            kv[k] = v

    name = canon_name(kv.get('name', 'player'))
    score = int(float(kv.get('score', '0')))
    ts = int(kv.get('ts', '0'))

    entry = {'name': name, 'score': score, 'ts': ts, 'user': args.user}
    data.setdefault('scores', []).append(entry)

    data['scores'] = sorted(data['scores'], key=lambda e: (-int(e['score']), int(e['ts'])))[:500]
    data['updatedAt'] = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    best_table, total_table = compute_tables(data['scores'])
    best_rank = next((i for i, (n, s) in enumerate(best_table, 1) if n == name and s == max([int(x['score']) for x in data['scores'] if x['name'] == name])), None)
    total_rank = next((i for i, (n, _) in enumerate(total_table, 1) if n == name), None)

    print(f'ENTRY {name} {score}')
    print(f'BEST_RANK {best_rank}')
    print(f'TOTAL_RANK {total_rank}')
    print('BEST_TOP')
    for i, (n, s) in enumerate(best_table[:10], 1):
        print(f'{i}. {n} — {s}')
    print('TOTAL_TOP')
    for i, (n, s) in enumerate(total_table[:10], 1):
        print(f'{i}. {n} — {s}')


if __name__ == '__main__':
    main()
