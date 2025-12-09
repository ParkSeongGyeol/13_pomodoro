import unittest
import sys
import os

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from planner import SessionPlanner

class TestSessionPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = SessionPlanner()

    def test_too_short_duration(self):
        # Less than 20 mins -> Empty schedule
        schedule = self.planner.generate_schedule(15)
        self.assertEqual(len(schedule), 0)

    def test_warmup_only(self):
        # 25 mins: Warmup (15) + Break (5) + Remainder (~5) -> Wrapup
        # 15+5 = 20 used. 5 left.
        # Logic: 
        # 1. Warmup (15 work)
        # 2. Break (5 break)
        # Rem: 5. Loop 2 needs 30.
        # Rem: 5. Loop 3 needs 10 check? 
        # Actually logic is: if rem >= 10 -> Wrapup. 5 < 10. So it ends.
        
        schedule = self.planner.generate_schedule(25)
        self.assertEqual(len(schedule), 2) 
        self.assertEqual(schedule[0]['type'], 'WORK')
        self.assertEqual(schedule[0]['duration'], 15*60)
        self.assertEqual(schedule[1]['type'], 'BREAK')

    def test_one_hour_session(self):
        # 60 mins logic:
        # 1. Warmup (15) -> Rem 45
        # 2. Break (5) -> Rem 40
        # 3. Medium Phase: 40 >= 30.
        #    Medium (25) -> Rem 15
        #    Break (5) -> Rem 10
        # 4. Peak: 10 < 25. Skip.
        # 5. Cool: 10 >= 10. Wrapup (10).
        
        schedule = self.planner.generate_schedule(60)
        self.assertEqual(len(schedule), 5)
        self.assertEqual(schedule[0]['label'], "Warm-up 🏃")
        self.assertEqual(schedule[2]['label'], "Build-up 📈") # logic changed
        self.assertEqual(schedule[4]['label'], "Wrap-up 🏁")

    def test_long_session(self):
        # 120 mins
        # 1. Warmup 20 used. Rem 100.
        # 2. Medium 30 used. Rem 70.
        # 3. Peak: 70 >= 50. Deep Focus (40) + Break (10). Rem 20.
        # 4. Peak loop: 20 < 25. Stop.
        # 5. Cool: 20 > 10. Wrapup.
        
        schedule = self.planner.generate_schedule(120)
        labels = [s['label'] for s in schedule]
        self.assertIn("Deep Focus 🔥", labels) # 40m
        self.assertIn("Build-up 📈", labels) # 25m
        self.assertIn("Wrap-up 🏁", labels)

if __name__ == '__main__':
    unittest.main()
