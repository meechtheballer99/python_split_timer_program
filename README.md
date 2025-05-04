Here's a quick and clear `README.md` for your terminal-based split timer program:

---

### 📘 README.md

```markdown
# 🏃 Track & Cross Country Split Timer (Terminal Version)

A Python-based terminal app for coaches to track and analyze athlete split times during races and workouts.

---

## 🔧 Features

- Track multiple athlete timers by name.
- Record splits interactively via terminal.
- Automatically sort athletes by:
  - Number of splits (desc)
  - Total time (asc)
- Group support (athletes can be in multiple groups).
- Synchronized split updates across groups.
- Save split results and analysis to Excel on exit.

---

## 📁 Project Structure

```

split\_timer\_project/
├── config.json             # Define athletes and groups
├── main.py                 # Main logic for split tracking
├── data/                   # Auto-created for Excel output
│   ├── splits\_<timestamp>.xlsx
│   └── analysis\_<timestamp>.xlsx

````

---

## ⚙️ Setup Instructions

### 1. Create a virtual environment
```bash
python -m venv split_timer_python_venv
````

### 2. Activate the virtual environment

#### On Windows (PowerShell):

```powershell
& "split_timer_python_venv\Scripts\Activate.ps1"
```

> ⚠️ If activation fails, run:
>
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

#### On macOS/Linux:

```bash
source split_timer_python_venv/bin/activate
```

### 3. Install dependencies

```bash
pip install pandas openpyxl
```

---

## 🏁 Usage

### 1. Set up your `config.json`:

```json
{
  "groups": {
    "default": ["Alice", "Bob", "Charlie"],
    "varsity": ["Alice", "David"]
  }
}
```

### 2. Run the program

```bash
python main.py
```

### 3. Terminal Commands:

* `split <name>` — record a split for that athlete.
* `status` — view current split counts and times.
* `quit` — record final splits and save Excel files.

---

## 📊 Output Files

Saved to the `/data/` folder:

* `splits_<timestamp>.xlsx`: Raw split data.
* `analysis_<timestamp>.xlsx`: Stats like average split, standard deviation, etc.

---

## 📌 Notes

* Timers auto-sync if an athlete is in multiple groups.
* On exit, a final split is recorded for all athletes automatically.

---

## ✅ Future Enhancements

* GUI with clickable split buttons.
* Chart visualizations of performance.
* Real-time group filtering in UI.

```

---

Let me know if you'd like a version with setup badges or GitHub formatting improvements!
```
