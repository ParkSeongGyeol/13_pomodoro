import tkinter as tk
from tkinter import messagebox
import threading
import time
from PIL import Image, ImageDraw
import pystray
import os
import queue
import csv
from datetime import datetime
from planner import SessionPlanner
import random
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller/Nuitka """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # Nuitka also supports this if structured correctly or we can use __file__ dir
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("집중 타이머")
        self.root.geometry("350x550") # Increased height for new UI
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Icon Setup
        icon_path = resource_path(os.path.join("assets", "icon.ico"))
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
            self.icon_path = icon_path # Store for tray
        else:
            self.icon_path = None

        # Logic / State 
        self.planner = SessionPlanner()
        self.schedule = [] # List of steps
        self.current_step_index = -1
        
        self.work_time = 25 * 60 
        self.break_time = 5 * 60
        
        self.is_break = False 
        self.running = False
        self.timer_id = None
        self.time_left = self.work_time
        
        # Thread safety queue
        self.queue = queue.Queue()

        self.WORKOUT_TIPS = [
            "팔굽혀펴기 20회 실시! 💪",
            "스쿼트 15회! 🦵",
            "목 스트레칭을 해주세요 🦒",
            "어깨를 돌려주세요 🙆‍♂️",
            "허리를 펴고 기지개를 켜세요 🧘‍♂️",
            "눈을 감고 1분간 휴식하세요 👁️",
            "물 한 잔 마시기 💧",
            "제자리 걸음 1분 🏃‍♂️"
        ]

        self.setup_ui()
        self.setup_tray_icon()
        self.process_queue()
        
        # Default to 1 Hour Plan
        self.root.after(100, lambda: self.start_smart_plan(60))

    def setup_ui(self):
        # --- Mode / Status (Step Info) ---
        self.mode_label = tk.Label(self.root, text="기본 모드", font=("Helvetica", 12, "bold"), fg="#333")
        self.mode_label.pack(pady=(10, 0))

        # --- Overtime Label (Red, Hidden Initially) ---
        self.overtime_label = tk.Label(self.root, text="+00:00", font=("Arial", 10, "bold"), fg="red")
        # Don't pack immediately, only when needed

        # --- Timer ---
        self.time_label = tk.Label(self.root, text=self.format_time(self.time_left), font=("Helvetica", 48))
        self.time_label.pack(pady=5)
        
        # --- Workout Tip Label ---
        self.workout_label = tk.Label(self.root, text="", font=("Arial", 10, "italic"), fg="#00796b")
        self.workout_label.pack(pady=(0, 10))

        # --- Controls ---
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        self.start_button = tk.Button(button_frame, text="집중 시작", command=self.start_timer, width=12, bg="#e1e1e1")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="일시정지", command=self.stop_timer, state=tk.DISABLED, width=10)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(button_frame, text="리셋", command=self.reset_timer, state=tk.DISABLED, width=10)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # --- Distraction ---
        self.distraction_btn = tk.Button(self.root, text="딴짓 했음... 😓", command=self.log_distraction, bg="#ffebee", fg="#c62828")
        self.distraction_btn.pack(pady=10, fill=tk.X, padx=50)

        # --- Smart Plan Section ---
        plan_frame = tk.LabelFrame(self.root, text="스마트 세션 플래너 🎓", padx=10, pady=10)
        plan_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # Navigation Buttons (Added)
        nav_frame = tk.Frame(plan_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(nav_frame, text="< 이전", command=self.prev_step, width=8).pack(side=tk.LEFT, padx=2)
        tk.Label(nav_frame, text="단계 이동", font=("Arial", 8), fg="gray").pack(side=tk.LEFT, expand=True)
        tk.Button(nav_frame, text="건너뛰기 >", command=self.skip_step, width=8).pack(side=tk.RIGHT, padx=2)
        
        tk.Label(plan_frame, text="총 가용 시간:").pack(anchor=tk.W)
        
        # Presets
        preset_frame = tk.Frame(plan_frame)
        preset_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(preset_frame, text="1시간", command=lambda: self.start_smart_plan(60), width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(preset_frame, text="2시간", command=lambda: self.start_smart_plan(120), width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(preset_frame, text="3시간", command=lambda: self.start_smart_plan(180), width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(preset_frame, text="4시간", command=lambda: self.start_smart_plan(240), width=6).pack(side=tk.LEFT, padx=2)
        
        # Custom Input
        custom_frame = tk.Frame(plan_frame)
        custom_frame.pack(fill=tk.X, pady=5)
        tk.Label(custom_frame, text="직접 입력 (분):").pack(side=tk.LEFT)
        self.custom_entry = tk.Entry(custom_frame, width=8)
        self.custom_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(custom_frame, text="확인", command=self.start_custom_plan, width=5).pack(side=tk.LEFT)
        
        # Progress / Queue Status
        self.plan_status_label = tk.Label(self.root, text="활성 플랜 없음", font=("Arial", 9), fg="gray")
        self.plan_status_label.pack(pady=5)

        # --- Footer ---
        self.info_label = tk.Label(self.root, text="최소화하면 트레이로 숨겨집니다", font=("Arial", 8), fg="gray")
        self.info_label.pack(side=tk.BOTTOM, pady=5)
        
        self.root.bind("<Unmap>", self.minimize_to_tray)

    # ... [Keep process_queue, format_time provided earlier] ...

    def process_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg == "SHOW":
                    self.perform_restore()
                elif msg == "QUIT":
                    self.perform_quit()
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02}:{secs:02}"
    
    # --- Planner Logic ---
    def start_custom_plan(self):
        try:
            val = int(self.custom_entry.get())
            self.start_smart_plan(val)
        except ValueError:
            messagebox.showerror("오류", "유효한 분(숫자)을 입력해주세요.")

    def start_smart_plan(self, minutes):
        self.schedule = self.planner.generate_schedule(minutes)
        if not self.schedule:
            messagebox.showwarning("시간 부족", "의미 있는 세션을 갖기에 시간이 너무 짧습니다.")
            return
            
        self.current_step_index = -1
        self.next_step() 

    def next_step(self):
        self._load_step_by_index(self.current_step_index + 1)

    def prev_step(self):
        if self.schedule and self.current_step_index > 0:
            self._load_step_by_index(self.current_step_index - 1)
            
    def skip_step(self):
        if self.schedule and self.current_step_index < len(self.schedule) - 1:
            self._load_step_by_index(self.current_step_index + 1)
            
    def _load_step_by_index(self, index):
        if index < len(self.schedule):
            self.current_step_index = index
            step = self.schedule[self.current_step_index]
            
            # Reset Overtime (Navigation should clear it)
            self.stop_overtime()

            # Set State
            self.is_break = (step['type'] == 'BREAK')
            self.time_left = step['duration']
            
            # Update UI
            label_text = f"단계 {self.current_step_index + 1}/{len(self.schedule)}: {step['label']}"
            self.mode_label.config(text=label_text, fg="#00796b" if not self.is_break else "#c62828")
            self.time_label.config(text=self.format_time(self.time_left), fg="black")
            
            # Workout Tip
            if self.is_break:
                tip = random.choice(self.WORKOUT_TIPS)
                self.workout_label.config(text=f"팁: {tip}")
            else:
                self.workout_label.config(text="")
            
            # Update Buttons
            btn_text = ("휴식" if self.is_break else "집중") + " 시작"
            self.start_button.config(text=btn_text, state=tk.NORMAL, bg="#c8e6c9" if self.is_break else "#e1e1e1")
            
            # Distraction Button Visibilty
            if self.is_break:
                self.distraction_btn.pack_forget()
            else:
                self.distraction_btn.pack(pady=10, fill=tk.X, padx=50)

            self.update_plan_status()
        else:
            # Plan Finished
            self.schedule = []
            self.stop_overtime()
            self.mode_label.config(text="플랜 완료! 🎉", fg="blue")
            self.time_label.config(text="00:00", fg="black")
            self.start_button.config(text="완료", state=tk.DISABLED)
            self.workout_label.config(text="")
            self.plan_status_label.config(text="모든 단계 종료.")

    def update_plan_status(self):
        remaining = len(self.schedule) - (self.current_step_index + 1)
        self.plan_status_label.config(text=f"남은 단계: {remaining}개")

    # --- Overtime Logic ---
    def start_overtime(self):
        self.overtime_start = datetime.now()
        self.overtime_label.pack(after=self.mode_label, pady=5) # Show it
        self.update_overtime()
        
    def stop_overtime(self):
        if hasattr(self, 'overtime_start'):
            del self.overtime_start
        self.overtime_label.pack_forget() # Hide it

    def update_overtime(self):
        if hasattr(self, 'overtime_start'):
            elapsed = datetime.now() - self.overtime_start
            total_seconds = int(elapsed.total_seconds())
            mins, secs = divmod(total_seconds, 60)
            self.overtime_label.config(text=f"+{mins:02}:{secs:02}")
            self.root.after(1000, self.update_overtime)

    # --- Timer Logic Updates ---
    def start_timer(self):
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            
            if self.is_break:
                self.distraction_btn.pack_forget() 
            
            # Verify overtime is cleared
            self.stop_overtime()
            
            self.run_timer()

    def stop_timer(self):
        if self.running:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None

    def reset_timer(self):
        self.stop_timer()
        self.stop_overtime()
        # If in a plan, reset to start of *current step*
        if self.schedule and 0 <= self.current_step_index < len(self.schedule):
            step = self.schedule[self.current_step_index]
            self.time_left = step['duration']
        else:
            # Fallback to standard 25/5
            self.time_left = self.break_time if self.is_break else self.work_time
            
        self.time_label.config(text=self.format_time(self.time_left), fg="black")
        self.reset_button.config(state=tk.DISABLED)

    def run_timer(self):
        if self.running and self.time_left > 0:
            self.time_left -= 1
            self.time_label.config(text=self.format_time(self.time_left))
            self.timer_id = self.root.after(1000, self.run_timer)
        elif self.time_left == 0:
            self.finish_timer()

    def finish_timer(self):
        self.running = False
        self.stop_button.config(state=tk.DISABLED)
        
        # Restore window
        if self.root.state() == 'withdrawn':
            self.perform_restore()
        
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()
        self.root.update()
        
        # Time ended logic:
        # 1. If in plan -> Move to next step (Prepare it) BUT don't start.
        if self.schedule:
             # Check if there is a next step
             if self.current_step_index < len(self.schedule) - 1:
                 self.next_step() # Loads next step (Title, Duration)
                 # Now start Overtime to show "latency since finish"
                 self.start_overtime()
             else:
                 # Plan complete
                 self.next_step() # Shows "Plan Completed"
        else:
            # Legacy loop
            self.toggle_mode_legacy()
            self.start_overtime()

    def toggle_mode_legacy(self):
        if not self.is_break:
            self.is_break = True
            self.time_left = self.break_time
            self.mode_label.config(text="휴식 시간! ☕", fg="green")
            self.start_button.config(text="휴식 시작", state=tk.NORMAL, bg="#c8e6c9")
            
            tip = random.choice(self.WORKOUT_TIPS)
            self.workout_label.config(text=f"팁: {tip}")
            
            self.distraction_btn.pack_forget()
        else:
            self.is_break = False
            self.time_left = self.work_time
            self.mode_label.config(text="업무 세션 🚀", fg="#333")
            self.start_button.config(text="업무 시작", state=tk.NORMAL, bg="#e1e1e1")
            self.workout_label.config(text="")
            self.distraction_btn.pack(pady=10, fill=tk.X, padx=50)

    def log_distraction(self):
        if not self.is_break and self.running:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            remaining = self.format_time(self.time_left)
            file_exists = os.path.isfile("focus_log.csv")
            with open("focus_log.csv", "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Timestamp", "TimeRemaining"])
                writer.writerow([now, remaining])
            orig_text = self.distraction_btn.cget("text")
            self.distraction_btn.config(text="기록됨!", state=tk.DISABLED)
            self.root.after(1000, lambda: self.distraction_btn.config(text=orig_text, state=tk.NORMAL))

    # --- Tray Icon Logic (Unchanged) ---
    def create_image(self):
        if self.icon_path and os.path.exists(self.icon_path):
            return Image.open(self.icon_path)
        
        # Fallback if no icon
        width = 64
        height = 64
        color1 = "black"
        color2 = "white"
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
        dc.rectangle((0, height // 2, width // 2, height), fill=color2)
        return image

    def setup_tray_icon(self):
        self.tray_icon = None

    def minimize_to_tray(self, event=None):
        if self.root.state() == 'iconic':
            self.root.withdraw()
            if not self.tray_icon:
                image = self.create_image()
                menu = (pystray.MenuItem('Show', self.on_tray_show, default=True),
                        pystray.MenuItem('Quit', self.on_tray_quit))
                self.tray_icon = pystray.Icon("name", image, "Focus Timer", menu)
                threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def on_tray_show(self, icon=None, item=None):
        self.queue.put("SHOW")

    def on_tray_quit(self, icon=None, item=None):
        self.queue.put("QUIT")

    def stop_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def perform_restore(self):
        self.root.deiconify()
        self.stop_tray_icon()
        self.root.state('normal')

    def perform_quit(self):
        self.stop_tray_icon()
        self.root.destroy()
        os._exit(0)

    def on_close(self):
        self.perform_quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
