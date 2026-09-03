# Surf Heat Manager

Surf competition management web app for Escola de Surf Peniche.
IB Computer Science Internal Assessment project.

## Stack

- Frontend: plain HTML, CSS, JavaScript (no framework, no npm, no CDN)
- Backend: Python with Flask
- Database: SQLite

## Running it

You need Python 3. Everything else the project uses (SQLite, the browser)
is already on the computer.

**Windows**

1. Install Python from python.org, and tick **Add python.exe to PATH** on the
   first screen of the installer.
2. Open the project folder in File Explorer, then type `cmd` in the address
   bar and press Enter. This opens Command Prompt already in that folder.
3. Run these two commands:

```
pip install -r requirements.txt
python app.py
```

**macOS and Linux**

```
pip3 install -r requirements.txt
python3 app.py
```

Then open http://localhost:5000 in any browser. Press Ctrl+C in the terminal
to stop the server.

The default director account is `director` / `surf2024`. Viewers do not log in
and only see the leaderboard.

### If it does not start

- **`No such file or directory: 'schema.sql'`** - the terminal is not in the
  project folder. Use `cd` to move into it, then run the command again.
- **`'python' is not recognized`** (Windows) - Python was installed without
  being added to PATH. Either reinstall with that box ticked, or use `py`
  instead of `python`.
- **`Address already in use`** - something else is using port 5000. Change
  the last line of `app.py` to a different number, such as `port=5001`, and
  open http://localhost:5001 instead.

The database file `surf.db` is created in the project folder the first time
the program runs. Deleting it starts a fresh competition.

## Files

| File | What it does |
| --- | --- |
| `app.py` | Flask routes joining the browser to the managers |
| `database.py` | SQLite connection, password hashing, first-run setup |
| `models.py` | `Surfer`, `Heat`, `WaveScore`, `ForecastSlot` |
| `heat_manager.py` | Algorithm 1: the heat draw |
| `score_manager.py` | Algorithms 2 and 3: scoring, ranking, progression |
| `forecast_manager.py` | Algorithm 4: forecast slot ranking |
| `schema.sql` | Every table. All database changes go here |
| `templates/index.html` | The six screens |
| `static/app.js` | Fetch calls and screen drawing |
| `static/style.css` | Screen styles and the print rules |

## Algorithms

1. **Heat draw.** Surfers are sorted by skill and dealt into heats in a snake
   order so skill is spread evenly, then the program repeatedly makes the
   smallest-skill-change swap that removes a group clash.
2. **Scoring.** A wave is judged 0-10 and multiplied by a difficulty weight
   (1.0 to 1.3); a surfer's heat total is their two best weighted waves added.
3. **Progression and tie-break.** Surfers are ranked by heat total, ties broken
   by best single wave, then by fewest waves ridden; the top N advance.
4. **Forecast ranking.** Each slot scores 0-1 on how close its wave height and
   tide are to ideal, combined 60% wave height to 40% tide.
5. **Heat sheet.** A table per heat, with a `@media print` rule that hides the
   menus and buttons so only the tables reach the A4 page.

## Conventions

- Keep the frontend dependency-free — no npm packages, no CDN frameworks.
- Database changes go through `schema.sql`; don't write ad-hoc migrations.
- Match the existing naming in the schema (heats, surfers, scores) rather than
  inventing new terms.
