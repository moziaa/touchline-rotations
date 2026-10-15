import json
import subprocess
import sys
import unittest
from pathlib import Path
from touchline import plan

class RotationTests(unittest.TestCase):
    def config(self, n=8, slots=5, segments=6):
        return dict(players=[{'name': f'P{i}'} for i in range(n)], on_field=slots,
                    segments=segments, minutes_per_segment=5)

    def test_balance_and_capacity_across_sizes(self):
        for n in range(2, 20):
            for slots in range(1, n+1):
                r = plan(self.config(n, slots))
                self.assertLessEqual(max(r['minutes'].values())-min(r['minutes'].values()), 5)
                self.assertEqual(sum(r['minutes'].values()), slots*6*5)
                for row in r['rounds']:
                    self.assertEqual(len(set(row['field'])), slots)
                    self.assertFalse(set(row['field']) & set(row['bench']))

    def test_availability_and_shortage(self):
        c = self.config(3, 3, 3)
        c['players'][0].update({'from': 2, 'through': 2})
        r = plan(c)
        self.assertNotIn('P0', r['rounds'][0]['field'])
        self.assertIn('P0', r['rounds'][1]['field'])
        self.assertNotIn('P0', r['rounds'][2]['field'])
        self.assertEqual(len(r['warnings']), 2)
        self.assertEqual(r['minutes']['P0'], 5)

    def test_invalid_inputs(self):
        for value in (0, -1, True, 1.5, 121, '5'):
            c = self.config()
            c['on_field'] = value
            with self.assertRaises(ValueError): plan(c)
        for players in ([], [{'name': 'A'}, {'name': 'a'}], [{'name': ' '}],
                        [{'name': 'A', 'from': 4, 'through': 2}]):
            with self.assertRaises(ValueError): plan(dict(players=players))

    def test_deterministic_without_mutation(self):
        c = self.config()
        before = json.dumps(c)
        self.assertEqual(plan(c), plan(c))
        self.assertEqual(before, json.dumps(c))

    def test_cli_example(self):
        root = Path(__file__).resolve().parent
        result = subprocess.run([sys.executable, str(root/'touchline.py'),
                                 str(root/'example.json'), '--json'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)['rounds']), 6)

if __name__ == '__main__': unittest.main()
