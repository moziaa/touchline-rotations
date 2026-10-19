import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from touchline import csv_text, plan

class CsvExportTests(unittest.TestCase):
    def test_round_trip_special_names_and_availability(self):
        result = plan({'on_field': 1, 'segments': 2, 'players': [
            {'name': 'Comet, Jr.'}, {'name': 'The "Rocket"', 'from': 2}]})
        rows = list(csv.DictReader(io.StringIO(csv_text(result))))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]['Nickname'], 'Comet, Jr.')
        self.assertEqual(rows[1]['Nickname'], 'The "Rocket"')
        self.assertEqual(rows[1]['Status'], 'Field')
        self.assertEqual(rows[2]['Status'], 'Bench')
        self.assertEqual(rows[1]['Start minute'], '5')

    def test_formula_like_names_are_text(self):
        for name in ('=1+1', '+123', '-123', '@SUM(A1)', '  =1+1'):
            with self.subTest(name=name):
                result = plan({'players': [{'name': name}], 'on_field': 1, 'segments': 1})
                rows = list(csv.reader(io.StringIO(csv_text(result))))
                self.assertEqual(rows[1][3], "'" + name.strip())

    def test_shortage_warning_stays_off_stdout(self):
        script = Path(__file__).resolve().with_name('touchline.py')
        with tempfile.TemporaryDirectory() as directory:
            roster = Path(directory)/'input.json'
            roster.write_text(json.dumps({'players': [{'name': 'A'}], 'on_field': 2, 'segments': 1}))
            result = subprocess.run([sys.executable, str(script), str(roster), '--csv'],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertIn('unfilled', result.stderr)
            self.assertNotIn('WARNING', result.stdout)
            self.assertEqual(len(list(csv.reader(io.StringIO(result.stdout)))), 2)
            conflict = subprocess.run([sys.executable, str(script), str(roster), '--csv', '--json'],
                                      capture_output=True, text=True, timeout=10)
            self.assertEqual(conflict.returncode, 2)
            self.assertEqual(conflict.stdout, '')

if __name__ == '__main__': unittest.main()
