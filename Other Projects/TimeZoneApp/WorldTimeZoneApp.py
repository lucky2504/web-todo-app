

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pytz


class TimezonesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("World Time Zones")

        # Common timezones
        self.timezones = [
            'America/Los_Angeles',  # Seattle
            'America/Chicago',  # Austin/Chicago
            'America/New_York',  # New York/Atlanta
            'Europe/Paris',  # Paris
            'Europe/London',  # London
            'Europe/Berlin',  # Berlin
            'Asia/Kolkata',  # Delhi
            'Asia/Singapore',  # Singapore
            'Asia/Tokyo',  # Tokyo
            'Australia/Sydney'  # Sydney
        ]

        # City names to display
        self.city_names = [
            'Seattle', 'Austin/Chicago', 'New York/Atlanta', 'Paris', 'London',
            'Berlin', 'Delhi', 'Singapore', 'Tokyo', 'Sydney'
        ]

        # Create and pack widgets
        for tz in self.timezones:
            frame = ttk.Frame(root, padding="10")
            frame.pack(fill=tk.X)

            city = self.city_names[self.timezones.index(tz)]
            ttk.Label(frame, text=f"{city}:").pack(side=tk.LEFT)

            time_label = ttk.Label(frame, text="")
            time_label.pack(side=tk.RIGHT)
            setattr(self, f"{tz}_label", time_label)

        self.update_time()

    def update_time(self):
        for tz in self.timezones:
            timezone = pytz.timezone(tz)
            current_time = datetime.now(timezone)
            time_str = current_time.strftime("%d %b %Y %H:%M")
            label = getattr(self, f"{tz}_label")
            label.config(text=time_str)

        # Update every second
        self.root.after(1000, self.update_time)


def main():
    root = tk.Tk()
    root.geometry("400x400")
    app = TimezonesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
