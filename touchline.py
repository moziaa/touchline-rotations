"""Local soccer rotation planner. No dependencies or network requests."""
import argparse
import json
from pathlib import Path


def positive(value, label):
    if type(value) is not int or not 1 <= value <= 120:
        raise ValueError(f'{label} must be an integer from 1 to 120')
    return value


def plan(config):
    if not isinstance(config, dict):
        raise ValueError('Configuration must be an object')
    slots = positive(config.get('on_field', 5), 'on_field')
    segments = positive(config.get('segments', 6), 'segments')
    minutes = positive(config.get('minutes_per_segment', 5), 'minutes_per_segment')
    players = config.get('players')
    if not isinstance(players, list) or not 1 <= len(players) <= 100:
        raise ValueError('players must contain 1 to 100 player objects')
    roster, seen = [], set()
    for player in players:
        if not isinstance(player, dict):
            raise ValueError('Each player must be an object')
        name = player.get('name')
        if not isinstance(name, str) or not name.strip() or len(name) > 40 or any(ord(c) < 32 for c in name):
            raise ValueError('Use a printable nickname of 1 to 40 characters')
        name = name.strip()
        if name.casefold() in seen:
            raise ValueError('Nicknames must be unique (ignoring case)')
        seen.add(name.casefold())
        start, end = player.get('from', 1), player.get('through', segments)
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= segments:
            raise ValueError(f'Invalid availability for {name}')
        roster.append((name, start, end))
    counts = {name: 0 for name, _, _ in roster}
    last = {name: -1 for name in counts}
    rounds, warnings = [], []
    for segment in range(1, segments + 1):
        available = [n for n, start, end in roster if start <= segment <= end]
        # Least minutes first, then longest since last appearance, then roster order.
        chosen = sorted(available, key=lambda n: (counts[n], last[n]))[:slots]
        for name in chosen:
            counts[name] += 1
            last[name] = segment
        if len(chosen) < slots:
            warnings.append(f'Segment {segment}: {slots - len(chosen)} unfilled field slots')
        rounds.append({'segment': segment, 'start_minute': (segment - 1) * minutes,
                       'end_minute': segment * minutes, 'field': chosen,
                       'bench': [n for n in available if n not in chosen]})
    return {'rounds': rounds, 'minutes': {n: c * minutes for n, c in counts.items()},
            'warnings': warnings}


def plain_text(result):
    lines = ['TOUCHLINE / MATCH ROTATIONS', '']
    for row in result['rounds']:
        lines.extend([f"{row['start_minute']:>3}-{row['end_minute']:<3} min | Segment {row['segment']}",
                      '  FIELD: ' + ', '.join(row['field']),
                      '  BENCH: ' + (', '.join(row['bench']) or 'Nobody'), ''])
    lines.append('PLANNED MINUTES')
    lines.extend(f'  {name}: {minutes}' for name, minutes in result['minutes'].items())
    lines.extend('WARNING: ' + warning for warning in result['warnings'])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('roster', type=Path)
    parser.add_argument('--json', action='store_true', help='Output machine-readable plan')
    args = parser.parse_args()
    try:
        result = plan(json.loads(args.roster.read_text(encoding='utf-8')))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2) if args.json else plain_text(result))
    return 1 if result['warnings'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
