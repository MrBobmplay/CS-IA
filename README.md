# Surf Heat Manager

Surf competition management web app for Escola de Surf Peniche.
IB Computer Science Internal Assessment project.

## Stack

- Frontend: plain HTML, CSS, JavaScript (no framework, no npm, no CDN)
- Backend: Python with Flask
- Database: SQLite

## Running it

```
pip install -r requirements.txt
python3 app.py
```

Then open http://localhost:5000.

The default director account is `director` / `surf2024`. Viewers do not log in
and only see the leaderboard.

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
