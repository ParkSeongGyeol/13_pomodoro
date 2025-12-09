import unittest
from unittest.mock import MagicMock
import sys
import os

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import PomodoroApp
import tkinter as tk

class TestPomodoro(unittest.TestCase):
    def setUp(self):
        # Mock Tkinter root
        self.root = MagicMock()
        # Mock queue to avoid threading issues in test
        self.root.after = MagicMock() 
        self.app = PomodoroApp(self.root)
        # Disable queue checking for unit tests
        self.app.process_queue = MagicMock()

    def test_initial_state(self):
        self.assertEqual(self.app.work_time, 25 * 60)
        self.assertEqual(self.app.time_left, 25 * 60)
        self.assertFalse(self.app.running)
        self.assertFalse(self.app.is_break)

    def test_start_timer(self):
        # We need to mock the buttons since they are configured in start_timer
        self.app.start_button = MagicMock()
        self.app.stop_button = MagicMock()
        self.app.reset_button = MagicMock()
        self.app.distraction_btn = MagicMock()
        
        self.app.start_timer()
        self.assertTrue(self.app.running)
        self.assertEqual(self.app.time_left, 25*60 - 1)

    def test_finish_timer_transition(self):
        # Mock GUI elements
        self.app.start_button = MagicMock()
        self.app.stop_button = MagicMock()
        self.app.mode_label = MagicMock()
        self.app.time_label = MagicMock()
        self.app.overtime_label = MagicMock()
        self.app.root.state = MagicMock(return_value="normal")
        self.app.root.attributes = MagicMock()
        self.app.distraction_btn = MagicMock()
        self.app.plan_status_label = MagicMock()
        
        # Setup a simple schedule
        self.app.schedule = [
            {'type': 'WORK', 'duration': 100, 'label': 'Step1'}, # Current
            {'type': 'BREAK', 'duration': 50, 'label': 'Step2'}  # Next
        ]
        self.app.current_step_index = 0
        self.app.is_break = False
        
        # Action: Finish Timer (End of Step1)
        self.app.finish_timer()
        
        # Expectation:
        # 1. Start Overtime (Red counter)
        self.app.overtime_label.pack.assert_called()
        # 2. State moved to Step 2 (Break)
        self.assertEqual(self.app.current_step_index, 1)
        self.assertTrue(self.app.is_break)
        # 3. Time label updated for Step 2
        self.app.time_label.config.assert_called_with(text="00:50", fg="black") # next step dur
        
        # 4. Timer NOT running (User must click Start)
        self.assertFalse(self.app.running)

    def test_navigation(self):
        # Setup specific schedule
        self.app.schedule = [
            {'type': 'WORK', 'duration': 100, 'label': 'Step1'},
            {'type': 'BREAK', 'duration': 50, 'label': 'Step2'}
        ]
        self.app.current_step_index = 0
        
        # Mock _load_step_by_index implicitly via navigation Logic
        self.app._load_step_by_index = MagicMock()
        
        # Test Skip
        self.app.skip_step()
        self.app._load_step_by_index.assert_called_with(1)
        
        # Test Prev
        self.app.current_step_index = 1
        self.app.prev_step()
        self.app._load_step_by_index.assert_called_with(0)
        
        # Test Bounds (Skip at end)
        self.app.current_step_index = 1
        self.app.skip_step() # Should not call for index 2
        # Mock call count check tricky here as it called previously. Reset mock.
        self.app._load_step_by_index.reset_mock()
        self.app.skip_step()
        self.app._load_step_by_index.assert_not_called()

    def test_overtime_logic(self):
         self.app.overtime_label = MagicMock()
         self.app.start_overtime()
         self.assertTrue(hasattr(self.app, 'overtime_start'))
         self.app.stop_overtime()
         self.assertFalse(hasattr(self.app, 'overtime_start'))
         self.app.overtime_label.pack_forget.assert_called()

    def test_log_distraction(self):
        import csv
        self.app.running = True
        self.app.is_break = False
        self.app.distraction_btn = MagicMock()
        self.app.time_left = 1234
        
        # Use a real file write test or mock open? Mock is cleaner but real is robust.
        # Let's mock open for safety in this environment
        with unittest.mock.patch("builtins.open", unittest.mock.mock_open()) as mock_file:
             with unittest.mock.patch("os.path.isfile", return_value=False):
                self.app.log_distraction()
                mock_file.assert_called_with("focus_log.csv", "a", newline="", encoding="utf-8")
                # Verify CSV writer was called (tricky with mock_open, check handle write)
                handle = mock_file()
                # We expect header + row
                self.assertEqual(handle.write.call_count, 2) 

    def test_reset_timer(self):
        self.app.stop_timer = MagicMock()
        self.app.reset_button = MagicMock()
        
        # Reset during WORK
        self.app.is_break = False
        self.app.time_left = 100
        self.app.reset_timer()
        self.assertEqual(self.app.time_left, 25 * 60)
        
        # Reset during BREAK
        self.app.is_break = True
        self.app.time_left = 100
        self.app.reset_timer()
        self.assertEqual(self.app.time_left, 5 * 60)

if __name__ == '__main__':
    unittest.main()
