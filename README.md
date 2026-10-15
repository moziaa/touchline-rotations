# Touchline Rotations ⚽

Less sideline arithmetic, more coaching. A small, offline soccer rotation planner that suggests who plays each segment and shows planned minutes.

This first release is a Python scheduling engine and printable text planner. A visual interface and position constraints are planned; they are not implemented yet.

## Try it

Requires Python 3.9+. No installation or external packages.

```sh
python3 touchline.py example.json
python3 touchline.py example.json > match-plan.txt
python3 touchline.py example.json --json
python3 -m unittest -v
```

Print match-plan.txt from any text editor. Example nicknames are fictional. Keep real rosters on your own device; the tool sends no data anywhere.

## Roster format

Copy example.json. Set `on_field` (all players on the field, including any goalkeeper), `segments`, and `minutes_per_segment`. Each player needs a unique `name`; optional `from` and `through` specify inclusive availability using segment numbers starting at 1. Omit them for full-match availability. Use short nicknames.

## How selection works

For each equal-length segment, available players with the fewest planned minutes are selected first. Ties favor those who played least recently, then roster order. Reorder nicknames to change initial tie preferences. With identical availability, minutes differ by at most one segment. With different availability, equal minutes are not guaranteed: late arrivals are prioritized when available. This is a transparent greedy suggestion, not a globally optimal schedule.

The tool reports unfilled field slots rather than silently inventing players. Exit codes: 0 = full plan, 1 = plan with shortages, 2 = invalid input. JSON output includes rounds, per-player minutes, and warnings.

There are no position assignments, goalkeeper restrictions, halftime rules, injury decisions, or live-match history yet. Changing the roster rebuilds the entire plan. The coach should review the plan and apply their league's rules.

## Next plays

- Visual rotation board with printable cards
- Preserve completed segments when someone arrives late
- Optional position and goalkeeper constraints with explicit conflict explanations
- Browser-local import/export

## Contributing

Keep the core dependency-free. Add regression tests for scheduling or validation changes. Run `python3 -m unittest -v` before publishing. MIT licensed.
