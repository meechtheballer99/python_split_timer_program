import tkinter as tk
from tkinter import ttk
import json
import time
import pandas as pd
import os
import threading
from collections import defaultdict
from datetime import datetime

# ---------------------- Timer Class ----------------------
class Timer:
    def __init__(self, name):
        self.name = name
        self.splits = []
        self.start_time = time.time()

    def split(self):
        now = time.time()
        elapsed = now - self.start_time
        if self.splits:
            split_time = elapsed - sum(self.splits)
        else:
            split_time = elapsed
        self.splits.append(split_time)

    def finalize(self):
        if not self.splits or time.time() - self.start_time > sum(self.splits):
            self.split()

    def total_time(self):
        return time.time() - self.start_time

    def last_split(self):
        return self.splits[-1] if self.splits else 0

    def current_split_time(self):
        return self.total_time() - sum(self.splits)

    def split_count(self):
        return len(self.splits)

# ---------------------- Utilities ----------------------
def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)

def create_group_timers(config):
    athlete_timers = {}
    group_timers = defaultdict(dict)

    for group, athletes in config['groups'].items():
        for athlete in athletes:
            if athlete not in athlete_timers:
                athlete_timers[athlete] = Timer(athlete)
            group_timers[group][athlete] = athlete_timers[athlete]

    return athlete_timers, group_timers

def sort_timers(timers):
    return sorted(timers, key=lambda t: (-t.split_count(), t.total_time()))

def save_to_excel(athlete_timers, group_timers=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_dir = os.path.join("data", "all_timers")
    os.makedirs(all_dir, exist_ok=True)

    # Combined raw splits
    raw_data = []
    for timer in sort_timers(athlete_timers.values()):
        row = {'Name': timer.name}
        for i, split in enumerate(timer.splits):
            row[f'Split {i+1}'] = split
        raw_data.append(row)
    pd.DataFrame(raw_data).to_excel(os.path.join(all_dir, f"all_splits_{timestamp}.xlsx"), index=False)

    # Combined analysis
    analysis_data = []
    for timer in sort_timers(athlete_timers.values()):
        if len(timer.splits) < 2:
            continue
        avg = sum(timer.splits) / len(timer.splits)
        std = pd.Series(timer.splits).std()
        row = {
            'Name': timer.name,
            'Average Split': avg,
            'Std Dev': std,
            'Number of Splits': len(timer.splits),
            'Total Time': timer.total_time()
        }
        analysis_data.append(row)
    pd.DataFrame(analysis_data).to_excel(os.path.join(all_dir, f"all_analysis_{timestamp}.xlsx"), index=False)

    # Per-group output
    if group_timers:
        for group_name, timers_dict in group_timers.items():
            group_dir = os.path.join("data", f"timer_group_{group_name.replace(' ', '_')}")
            os.makedirs(group_dir, exist_ok=True)

            raw_group = []
            analysis_group = []

            for timer in sort_timers(timers_dict.values()):
                row = {'Name': timer.name}
                for i, split in enumerate(timer.splits):
                    row[f'Split {i+1}'] = split
                raw_group.append(row)

                if len(timer.splits) >= 2:
                    avg = sum(timer.splits) / len(timer.splits)
                    std = pd.Series(timer.splits).std()
                    analysis_group.append({
                        'Name': timer.name,
                        'Average Split': avg,
                        'Std Dev': std,
                        'Number of Splits': len(timer.splits),
                        'Total Time': timer.total_time()
                    })

            pd.DataFrame(raw_group).to_excel(os.path.join(group_dir, f"splits_{timestamp}.xlsx"), index=False)
            pd.DataFrame(analysis_group).to_excel(os.path.join(group_dir, f"analysis_{timestamp}.xlsx"), index=False)

# ---------------------- Leaderboard ----------------------
class LeaderboardWindow:
    def __init__(self, root, athlete_timers, group_name):
        self.top = tk.Toplevel(root)
        self.top.title(f"{group_name} - Leaderboard")
        self.athlete_timers = athlete_timers

        self.tree = ttk.Treeview(
            self.top,
            columns=('Name', 'Splits', 'Total', 'Last Split', 'Current Split'),
            show='headings'
        )
        self.tree.heading('Name', text='Name')
        self.tree.heading('Splits', text='Splits')
        self.tree.heading('Total', text='Total Time')
        self.tree.heading('Last Split', text='Last Split')
        self.tree.heading('Current Split', text='Current Split')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.update_table()

    def update_table(self):
        self.tree.delete(*self.tree.get_children())
        for timer in sort_timers(self.athlete_timers.values()):
            self.tree.insert('', 'end', values=(
                timer.name,
                timer.split_count(),
                f"{timer.total_time():.2f}",
                f"{timer.last_split():.2f}",
                f"{timer.current_split_time():.2f}"
            ))
        self.top.after(1000, self.update_table)

# ---------------------- Main Timer GUI ----------------------
class TimerApp:
    def __init__(self, root, athlete_timers, group_name, all_timers, group_timers, on_done_all):
        self.root = root
        self.group_name = group_name
        self.athlete_timers = athlete_timers
        self.all_timers = all_timers
        self.group_timers = group_timers
        self.on_done_all = on_done_all
        self.row_widgets = {}

        self.root.title(f"{group_name} - Timer Control")
        self.root.geometry("750x550")

        self.canvas = tk.Canvas(root)
        self.scroll_y = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.frame = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        self.status_label = ttk.Label(root, text="")
        self.status_label.pack(pady=5)

        self.done_button = ttk.Button(root, text="Done (Save & Exit)", command=self.finalize_all_and_exit)
        self.done_button.pack(pady=10)

        self.frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.build_athlete_rows()
        self.update_live_times()

        self.leaderboard_window = LeaderboardWindow(root, self.athlete_timers, self.group_name)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def build_athlete_rows(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.row_widgets.clear()

        for timer in sort_timers(self.athlete_timers.values()):
            row = ttk.Frame(self.frame)
            row.pack(fill='x', padx=5, pady=2)

            name_lbl = ttk.Label(row, text=timer.name, width=12)
            name_lbl.pack(side='left')

            splits_lbl = ttk.Label(row, width=8)
            splits_lbl.pack(side='left')

            total_lbl = ttk.Label(row, width=12)
            total_lbl.pack(side='left')

            current_lbl = ttk.Label(row, width=14)
            current_lbl.pack(side='left')

            split_btn = ttk.Button(row, text="Split", command=lambda t=timer: self.record_split(t))
            split_btn.pack(side='left', padx=10)

            self.row_widgets[timer.name] = {
                'row': row,
                'splits': splits_lbl,
                'total': total_lbl,
                'current': current_lbl
            }

    def update_live_times(self):
        current_order = list(self.row_widgets.keys())
        new_order = [t.name for t in sort_timers(self.athlete_timers.values())]
        if current_order != new_order:
            self.build_athlete_rows()

        for timer in self.athlete_timers.values():
            widgets = self.row_widgets.get(timer.name)
            if widgets:
                widgets['splits'].config(text=f"{timer.split_count()}")
                widgets['total'].config(text=f"{timer.total_time():.2f}s")
                widgets['current'].config(text=f"{timer.current_split_time():.2f}s")

        self.root.after(500, self.update_live_times)

    def record_split(self, timer):
        timer.split()
        self.status_label.config(text=f"Split recorded for {timer.name}")
        self.build_athlete_rows()

    def finalize_all_and_exit(self):
        self.on_done_all()

# ---------------------- Launcher ----------------------
def run_gui():
    config = load_config("config.json")
    all_timers, group_timers = create_group_timers(config)
    windows = []

    def done_all():
        for timer in all_timers.values():
            timer.finalize()
        save_to_excel(all_timers, group_timers)
        for win in windows:
            win.quit()

    for group_name, group_timers_subset in group_timers.items():
        root = tk.Tk()
        app = TimerApp(root, group_timers_subset, group_name, all_timers, group_timers, on_done_all=done_all)
        windows.append(root)
        threading.Thread(target=root.mainloop, daemon=True).start()

    tk.mainloop()

# ---------------------- Entry ----------------------
if __name__ == "__main__":
    run_gui()
