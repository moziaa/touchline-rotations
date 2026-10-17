import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from match_sheet import render
from touchline import plan

class MatchSheetTests(unittest.TestCase):
    def test_escape_names_and_show_shortages(self):
        result = plan({'players': [{'name': '<script>alert(1)</script>'}], 'on_field': 2, 'segments': 1})
        html = render(result)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('1 unfilled field slots', html)
        self.assertIn('5 min', html)

    def test_all_rounds_and_totals_render(self):
        result = plan({'players': [{'name': 'Comet'}, {'name': 'Dash'}], 'on_field': 1, 'segments': 4})
        html = render(result)
        self.assertEqual(html.count('<article>'), 4)
        self.assertEqual(html.count('<meter '), 2)
        self.assertIn('15–20 min', html)
        self.assertNotIn('<aside>', html)
        self.assertNotIn('https://', html)

    def test_cli_preserves_existing_files(self):
        script = Path(__file__).resolve().with_name('match_sheet.py')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            roster, output = root/'roster.json', root/'plan.html'
            roster.write_text(json.dumps({'players': [{'name': 'A'}], 'on_field': 1}))
            command = [sys.executable, str(script), str(roster), str(output)]
            first = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = output.read_text()
            second = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(second.returncode, 2)
            self.assertEqual(output.read_text(), before)

if __name__ == '__main__': unittest.main()
