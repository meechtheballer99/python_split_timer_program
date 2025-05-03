import json
import time
import pandas as pd
import os
from collections import defaultdict
from datetime import datetime

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
        return sum(self.splits)

    def last_split(self):
        return self.splits[-1] if self.splits else 0

    def split_count(self):
        return len(self.splits)

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

def save_to_excel(athlete_timers):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("data", exist_ok=True)

    # Raw split data
    raw_data = []
    for timer in sort_timers(athlete_timers.values()):
        row = {'Name': timer.name}
        for i, split in enumerate(timer.splits):
            row[f'Split {i+1}'] = split
        raw_data.append(row)
    df_raw = pd.DataFrame(raw_data)
    df_raw.to_excel(f"data/splits_{timestamp}.xlsx", index=False)

    # Analysis
    analysis_data = []
    for timer in sort_timers(athlete_timers.values()):
        if len(timer.splits) < 2:
            continue
        diffs = [j - i for i, j in zip(timer.splits[:-1], timer.splits[1:])]
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
    df_analysis = pd.DataFrame(analysis_data)
    df_analysis.to_excel(f"data/analysis_{timestamp}.xlsx", index=False)


def main():
    config = load_config("config.json")
    athlete_timers, group_timers = create_group_timers(config)

    print("\nTimers initialized. Type 'split <name>' to record a split, 'status' to view status, 'quit' to exit.\n")

    while True:
        cmd = input("Command: ").strip()

        if cmd.lower() == 'quit':
            for timer in athlete_timers.values():
                timer.finalize()
            save_to_excel(athlete_timers)
            print("Splits saved. Goodbye!")
            break

        elif cmd.lower() == 'status':
            sorted_timers = sort_timers(athlete_timers.values())
            for t in sorted_timers:
                print(f"{t.name}: Splits={t.split_count()}, Total={t.total_time():.2f}, Last={t.last_split():.2f}")

        elif cmd.startswith("split"):
            parts = cmd.split()
            if len(parts) != 2:
                print("Usage: split <name>")
                continue
            name = parts[1]
            if name in athlete_timers:
                athlete_timers[name].split()
                print(f"Split recorded for {name}")
            else:
                print(f"No such athlete: {name}")

        else:
            print("Unknown command. Use 'split <name>', 'status', or 'quit'.")


if __name__ == "__main__":
    main()
