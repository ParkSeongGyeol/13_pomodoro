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
        # Less than 25 mins -> Empty schedule
        schedule = self.planner.generate_schedule(20)
        self.assertEqual(len(schedule), 0)

    def test_warmup_only(self):
        # 30 mins: Standard (25) + Break (5)
        schedule = self.planner.generate_schedule(30)
        self.assertEqual(len(schedule), 2) 
        self.assertEqual(schedule[0]['type'], 'WORK')
        self.assertEqual(schedule[0]['duration'], 25*60)
        self.assertEqual(schedule[1]['type'], 'BREAK')

    def test_one_hour_session(self):
        # 60 mins logic:
        # 1. Start (25) -> Rem 35
        # 2. Break (5) -> Rem 30
        # 3. Loop: 30 < 45 (for Peak). Fallback 25.
        #    Focus (25) > Rem 5
        #    Break (5) > Rem 0
        
        schedule = self.planner.generate_schedule(60)
        self.assertEqual(len(schedule), 4)
        self.assertEqual(schedule[0]['label'], "Standard Focus 🚀")
        self.assertEqual(schedule[2]['label'], "Focus 🧠")
        # No wrap up because exactly 0 left

    def test_long_session(self):
        # 120 mins
        # 1. Start (25) + Break (5) = 30 used. Rem 90.
        # 2. Loop 1: 90 >= 45. Peak (35) + Break (10). Rem 45.
        # 3. Loop 2: 45 >= 45. Peak (35) + Break (10). Rem 0.
        
        schedule = self.planner.generate_schedule(120)
        labels = [s['label'] for s in schedule]
        self.assertIn("Deep Focus 🔥", labels) # 35m
        self.assertEqual(labels.count("Deep Focus 🔥"), 2) 
        self.assertNotIn("Wrap-up 🏁", labels)

if __name__ == '__main__':
    unittest.main()
