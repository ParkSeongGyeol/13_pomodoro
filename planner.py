class SessionPlanner:
    def __init__(self):
        pass

    def generate_schedule(self, total_minutes):
        """
        Generates a schedule fitting into total_minutes.
        Pattern: Warmup (15) -> Medium (25) -> Peak (40) -> Cooldown.
        """
        schedule = []
        remaining_minutes = total_minutes
        
        # Minimum consistency check
        if remaining_minutes < 20:
            return []

        # 1. Warm-up Phase (15m Work + 5m Break)
        if remaining_minutes >= 20:
            schedule.append({"type": "WORK", "duration": 15 * 60, "label": "Warm-up 🏃"})
            remaining_minutes -= 15
            
            if remaining_minutes >= 5:
                schedule.append({"type": "BREAK", "duration": 5 * 60, "label": "Short Break ☕"})
                remaining_minutes -= 5
            else:
                return schedule

        # 2. Ramp-up Phase (Medium 25m)
        # Try to fit a medium session before peak if enough time
        # Need at least Medium(25) + Break(5) = 30m
        if remaining_minutes >= 30:
            schedule.append({"type": "WORK", "duration": 25 * 60, "label": "Build-up 📈"})
            remaining_minutes -= 25
            
            if remaining_minutes >= 5:
                schedule.append({"type": "BREAK", "duration": 5 * 60, "label": "Break 🌿"})
                remaining_minutes -= 5
            else:
                return schedule

        # 3. Peak Phase (40m)
        # We try to fit 40m blocks.
        while remaining_minutes >= 25: # At least a standard session
            # If enough for Peak (40 + 10 break)
            if remaining_minutes >= 50:
                work_min = 40
                break_min = 10
                schedule.append({"type": "WORK", "duration": work_min * 60, "label": "Deep Focus 🔥"})
            else:
                # Fallbck to 25m
                work_min = 25
                break_min = 5
                schedule.append({"type": "WORK", "duration": work_min * 60, "label": "Focus 🧠"})
            
            remaining_minutes -= work_min
            
            # Add break logic
            if remaining_minutes >= break_min:
                schedule.append({"type": "BREAK", "duration": break_min * 60, "label": "Break 🌿"})
                remaining_minutes -= break_min
            else:
                 # Remaining time is bonus break/buffer
                 break

        # 4. Cool-down / Wrap up
        if remaining_minutes >= 10:
             schedule.append({"type": "WORK", "duration": remaining_minutes * 60, "label": "Wrap-up 🏁"})
             remaining_minutes = 0

        return schedule
