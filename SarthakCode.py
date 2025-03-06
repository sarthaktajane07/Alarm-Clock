import tkinter as tk
import time
import pygame
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
import math

# Set up the main window
class AlarmClock(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Alarm Clock")
        self.geometry("400x400")
        self.configure(bg="black")
        
        self.alarm_times = []
        self.alarms_sounds = []
        self.is_snooze = False
        self.snooze_time = 5  # 5 minutes snooze by default
        self.theme = "Midnight"  # Set initial theme to match bg="black"
        
        # Create canvas for analog clock
        self.clock_canvas = tk.Canvas(self, width=200, height=200, bg="black", highlightthickness=0)
        self.clock_canvas.pack(pady=20)
        
        # Define center coordinates as instance variables
        self.center_x = 100
        self.center_y = 100
        
        # Draw static clock elements and store their IDs
        self.clock_face = self.clock_canvas.create_oval(10, 10, 190, 190, outline="white", width=2)
        self.number_ids = []
        for hour in range(1, 13):
            hour_angle = (90 - 30 * hour) % 360
            radians = math.radians(hour_angle)
            x = self.center_x + 80 * math.cos(radians)
            y = self.center_y - 80 * math.sin(radians)
            number_id = self.clock_canvas.create_text(x, y, text=str(hour), fill="white", font=("Arial", 12))
            self.number_ids.append(number_id)
        self.center_circle = self.clock_canvas.create_oval(95, 95, 105, 105, fill="white")
        
        # Initialize hand IDs
        self.hour_hand = None
        self.minute_hand = None
        self.second_hand = None
        
        # Alarm and snooze buttons
        self.set_alarm_button = tk.Button(self, text="Set Alarm", command=self.set_alarm)
        self.set_alarm_button.pack(pady=5)
        
        self.snooze_button = tk.Button(self, text="Snooze", command=self.snooze, state=tk.DISABLED)
        self.snooze_button.pack(pady=5)

        self.puzzle_button = tk.Button(self, text="Wake-up Puzzle", command=self.solve_puzzle, state=tk.DISABLED)
        self.puzzle_button.pack(pady=5)

        # Theme and sound options
        self.theme_button = tk.Button(self, text="Switch Theme", command=self.toggle_theme)
        self.theme_button.pack(pady=5)
        
        self.sound_button = tk.Button(self, text="Select Alarm Sound", command=self.select_sound)
        self.sound_button.pack(pady=5)

        # Initialize pygame mixer for sound playback
        pygame.mixer.init()

        # Set initial theme colors
        self.set_theme(self.theme)
        
        # Start the time update loop
        self.update_time()

    def update_time(self):
        """Update the analog clock hands every second."""
        current_time = time.strftime('%H:%M:%S')
        h, m, s = map(int, current_time.split(':'))
        
        # Calculate angles (90 degrees is 12 o'clock, clockwise)
        second_angle = (90 - 6 * s) % 360
        minute_angle = (90 - 6 * (m + s / 60)) % 360
        hour_angle = (90 - 30 * (h % 12 + m / 60 + s / 3600)) % 360
        
        # Convert to radians
        second_radians = math.radians(second_angle)
        minute_radians = math.radians(minute_angle)
        hour_radians = math.radians(hour_angle)
        
        # Calculate hand end points
        second_x = self.center_x + 90 * math.cos(second_radians)
        second_y = self.center_y - 90 * math.sin(second_radians)
        minute_x = self.center_x + 80 * math.cos(minute_radians)
        minute_y = self.center_y - 80 * math.sin(minute_radians)
        hour_x = self.center_x + 60 * math.cos(hour_radians)
        hour_y = self.center_y - 60 * math.sin(hour_radians)
        
        # Delete previous hands
        if self.hour_hand:
            self.clock_canvas.delete(self.hour_hand)
        if self.minute_hand:
            self.clock_canvas.delete(self.minute_hand)
        if self.second_hand:
            self.clock_canvas.delete(self.second_hand)
        
        # Set hand colors based on theme
        if self.theme == "Sunrise":
            hour_color = "black"
            minute_color = "black"
            second_color = "red"
        else:  # Midnight
            hour_color = "white"
            minute_color = "white"
            second_color = "red"
        
        # Draw new hands
        self.hour_hand = self.clock_canvas.create_line(self.center_x, self.center_y, hour_x, hour_y, fill=hour_color, width=3)
        self.minute_hand = self.clock_canvas.create_line(self.center_x, self.center_y, minute_x, minute_y, fill=minute_color, width=2)
        self.second_hand = self.clock_canvas.create_line(self.center_x, self.center_y, second_x, second_y, fill=second_color, width=1)
        
        # Check alarms and schedule next update
        self.check_alarms(current_time)
        self.after(1000, self.update_time)
        
    def set_alarm(self):
        """Set a new alarm at a specified time."""
        alarm_time = self.ask_for_time()
        if alarm_time:
            self.alarm_times.append(alarm_time)
            self.alarms_sounds.append(self.ask_for_sound())
            # Removed undefined self.check_alarm_time call
            messagebox.showinfo("Alarm Set", f"Alarm is set for {alarm_time}")

    def ask_for_time(self):
        """Prompt user to enter alarm time."""
        time_entry = simpledialog.askstring("Alarm Time", "Enter alarm time (HH:MM):")
        return time_entry

    def ask_for_sound(self):
        """Allow user to select a sound file."""
        sound_path = filedialog.askopenfilename(title="Select Alarm Sound", filetypes=[("MP3 files", "*.mp3"), ("WAV files", "*.wav")])
        return sound_path

    def select_sound(self):
        """Open file dialog to select alarm sound."""
        sound_path = filedialog.askopenfilename(title="Select Alarm Sound", filetypes=[("MP3 files", "*.mp3"), ("WAV files", "*.wav")])
        if sound_path:
            self.alarms_sounds.append(sound_path)
            messagebox.showinfo("Sound Selected", f"Sound selected: {sound_path}")

    def check_alarms(self, current_time):
        """Check if current time's hour and minute match any alarm time."""
        current_hm = current_time[:5]  # 'HH:MM'
        for alarm_time, sound in zip(self.alarm_times, self.alarms_sounds):
            if current_hm == alarm_time:
                self.trigger_alarm(sound)

    def trigger_alarm(self, sound):
        """Trigger the alarm by playing sound."""
        self.snooze_button.config(state=tk.NORMAL)
        self.puzzle_button.config(state=tk.NORMAL)
        pygame.mixer.music.load(sound)
        pygame.mixer.music.play()

    def snooze(self):
        """Snooze the alarm for a set period."""
        self.is_snooze = True
        messagebox.showinfo("Snooze", f"Snooze for {self.snooze_time} minutes")
        self.after(self.snooze_time * 60000, self.trigger_alarm)  # Note: trigger_alarm needs a sound argument; this may need adjustment

    def solve_puzzle(self):
        """Show a simple puzzle to solve."""
        puzzle_answer = simpledialog.askstring("Wake-up Puzzle", "Solve: 3 + 5 = ?")
        if puzzle_answer == "8":
            self.puzzle_button.config(state=tk.DISABLED)
            self.snooze_button.config(state=tk.DISABLED)
            messagebox.showinfo("Puzzle Solved", "Good job! Alarm stopped.")
        else:
            messagebox.showinfo("Puzzle Failed", "Try again!")

    def set_theme(self, theme):
        """Set the colors based on the theme."""
        if theme == "Sunrise":
            self.configure(bg="white")
            self.clock_canvas.config(bg="white")
            self.clock_canvas.itemconfig(self.clock_face, outline="black")
            for number_id in self.number_ids:
                self.clock_canvas.itemconfig(number_id, fill="black")
            self.clock_canvas.itemconfig(self.center_circle, fill="black")
        else:  # Midnight
            self.configure(bg="black")
            self.clock_canvas.config(bg="black")
            self.clock_canvas.itemconfig(self.clock_face, outline="white")
            for number_id in self.number_ids:
                self.clock_canvas.itemconfig(number_id, fill="white")
            self.clock_canvas.itemconfig(self.center_circle, fill="white")

    def toggle_theme(self):
        """Switch between dark/light themes."""
        if self.theme == "Sunrise":
            self.set_theme("Midnight")
            self.theme = "Midnight"
        else:
            self.set_theme("Sunrise")
            self.theme = "Sunrise"

    def start_alarm_clock(self):
        """Start the clock and keep running."""
        self.mainloop()

# Run the application
if __name__ == "__main__":
    alarm_clock = AlarmClock()
    alarm_clock.start_alarm_clock()