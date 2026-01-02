class SessionPlanner:
    def __init__(self):
        pass

    def generate_schedule(self, total_minutes):
        """
        Generates a schedule fitting into total_minutes.
        Pattern by User Request: 
        - Start: Standard (25m) -> Break (5m)
        - Peak: Reduced to 35m (from 40m) or 30m to keep focus sharp.
        """
        schedule = []
        remaining_minutes = total_minutes
        
        # Minimum requirement: At least 25m for one session
        if remaining_minutes < 25:
            return []

        # 1. Initial Phase (Standard 25m Work + 5m Break)
        # User requested 25m start.
        if remaining_minutes >= 25:
            schedule.append({"type": "WORK", "duration": 25 * 60, "label": "기본 집중 🚀"})
            remaining_minutes -= 25
            
            # Add break if we have enough time for at least a short next step or just a break
            if remaining_minutes >= 5:
                schedule.append({"type": "BREAK", "duration": 5 * 60, "label": "짧은 휴식 ☕"})
                remaining_minutes -= 5
            else:
                return schedule

        # 2. Peak / Flow Phase 
        # User requested peak time to be shorter (was 40m). Let's aim for 30-35m.
        # Let's try to fit 35m Peak blocks if possible.
        
        while remaining_minutes >= 25: # At least a standard session
            # If enough for Peak (35 + 10 break) = 45m
            if remaining_minutes >= 45:
                work_min = 35
                break_min = 10
                schedule.append({"type": "WORK", "duration": work_min * 60, "label": "깊은 집중 🔥"})
            else:
                # Fallback to Standard 25m
                work_min = 25
                break_min = 5
                schedule.append({"type": "WORK", "duration": work_min * 60, "label": "집중 🧠"})
            
            remaining_minutes -= work_min
            
            # Add break logic
            if remaining_minutes >= break_min:
                schedule.append({"type": "BREAK", "duration": break_min * 60, "label": "휴식 🌿"})
                remaining_minutes -= break_min
            else:
                 # If we can't fit a full break, just exit loop to wrap up
                 break

        # 3. Cool-down / Wrap up
        if remaining_minutes >= 10:
             schedule.append({"type": "WORK", "duration": remaining_minutes * 60, "label": "마무리 🏁"})
             remaining_minutes = 0

        return schedule
