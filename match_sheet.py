"""Render an offline, printable match sheet from a Touchline roster."""
import argparse
from html import escape
import json
from pathlib import Path
from touchline import plan


def render(result):
    cards = []
    for row in result['rounds']:
        field = ''.join('<li>' + escape(name) + '</li>' for name in row['field'])
        bench = escape(', '.join(row['bench']) or 'Nobody')
        cards.append(f"<article><p class='eyebrow'>SEGMENT {row['segment']}</p>"
                     f"<h2>{row['start_minute']}–{row['end_minute']} min</h2>"
                     f"<h3>On the field</h3><ul>{field}</ul><p class='bench'><b>Bench:</b> {bench}</p></article>")
    maximum = max(result['minutes'].values(), default=1) or 1
    bars = ''.join(f"<div class='player'><span>{escape(name)}</span>"
                   f"<meter min='0' max='{maximum}' value='{minutes}' aria-label='{escape(name, quote=True)} planned minutes'>{minutes}</meter>"
                   f"<b>{minutes} min</b></div>" for name, minutes in result['minutes'].items())
    warnings = ''.join('<li>' + escape(w) + '</li>' for w in result['warnings'])
    notice = '<aside><h2>Check before kickoff</h2><ul>' + warnings + '</ul></aside>' if warnings else ''
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Touchline — Match sheet</title><style>
*{box-sizing:border-box}body{margin:0;background:#eef3ec;color:#16342b;font:16px/1.5 system-ui,sans-serif}
main{max-width:1100px;margin:auto;padding:40px 24px}header{border-bottom:3px solid #16342b;margin-bottom:28px;padding-bottom:24px}
.eyebrow{font-size:12px;font-weight:800;letter-spacing:.16em;color:#456657}h1{font-size:clamp(32px,6vw,56px);line-height:1.1;margin:12px 0}h2{margin:6px 0 20px}h3{font-size:14px;margin:0 0 8px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}article{background:white;border:1px solid #c7d5c9;border-top:6px solid #277354;border-radius:10px;padding:20px;break-inside:avoid}
ul{padding-left:20px}article ul{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:7px}article li{padding:4px 10px;background:#e5f1d9;border-radius:5px}.bench{border-top:1px solid #ddd;padding-top:12px;font-size:14px}
.summary{background:white;padding:24px;margin-top:24px;border-radius:10px;break-inside:avoid}.player{display:grid;grid-template-columns:minmax(80px,1fr) 2fr 70px;gap:12px;align-items:center;margin:10px 0;overflow-wrap:anywhere}meter{width:100%;height:20px}aside{background:#fff0cc;padding:20px;margin-bottom:24px;border-left:5px solid #9a6000}footer{font-size:13px;margin-top:24px;color:#456657}li{overflow-wrap:anywhere}
@media print{body{background:white;color:black}main{padding:0}h1{font-size:30px}.grid{grid-template-columns:repeat(2,1fr)}article{border:1px solid #777}header{margin-bottom:16px}footer{color:black}a{color:inherit}}
</style></head><body><main><header><p class="eyebrow">TOUCHLINE / COACH'S MATCH SHEET</p>
<h1>More play. Less juggling.</h1><p>Suggested rotations • Equal-length segments • Review before kickoff</p></header>''' + notice + '<section class="grid" aria-label="Rotation schedule">' + ''.join(cards) + '</section><section class="summary"><h2>Planned playing time</h2>' + bars + '''</section><footer>Use your browser’s Print command to print or save as PDF. Minutes are suggestions, not position assignments. Apply your league’s rules. This file contains roster information: share only with intended recipients.</footer></main></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('roster', type=Path)
    parser.add_argument('output', type=Path, help='New HTML file; existing files are not overwritten')
    args = parser.parse_args()
    try:
        result = plan(json.loads(args.roster.read_text(encoding='utf-8')))
        with args.output.open('x', encoding='utf-8') as output:
            output.write(render(result))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f'Match sheet saved to {args.output}')
    return 1 if result['warnings'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
