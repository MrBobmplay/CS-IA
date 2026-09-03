"""Algorithms 2 and 3: wave scoring, heat totals, ranking and progression.

A wave is scored 0-10 by the judge and multiplied by a difficulty weight
(1.0 for a typical wave, up to 1.3 for a big or technical one). A surfer's
heat total is the sum of their two best weighted waves.
"""

import database
from heat_manager import heat_manager
from models import WaveScore

MAX_WEIGHT = 1.3


class ScoreManager:
    """Single shared owner of the wave score data."""

    def add_score(self, heat_id, surfer_id, raw_score, weight):
        """Record one wave ridden in a heat."""
        if not 0 <= raw_score <= 10:
            raise ValueError("A wave score must be between 0 and 10.")
        if not 1.0 <= weight <= MAX_WEIGHT:
            raise ValueError("The difficulty weight must be between 1.0 and %.1f." % MAX_WEIGHT)
        in_heat = database.query(
            "SELECT 1 FROM heat_surfers WHERE heat_id = ? AND surfer_id = ?",
            (heat_id, surfer_id))
        if not in_heat:
            raise ValueError("That surfer is not in that heat.")
        return database.run(
            "INSERT INTO scores (heat_id, surfer_id, raw_score, weight) VALUES (?, ?, ?, ?)",
            (heat_id, surfer_id, raw_score, weight))

    def get_scores(self, heat_id, surfer_id):
        rows = database.query(
            "SELECT * FROM scores WHERE heat_id = ? AND surfer_id = ? ORDER BY id",
            (heat_id, surfer_id))
        return [WaveScore(r["id"], r["heat_id"], r["surfer_id"], r["raw_score"], r["weight"])
                for r in rows]

    # ---- Algorithm 2 ----------------------------------------------------

    def heat_total(self, heat_id, surfer_id):
        """Sum of the surfer's two best weighted waves in this heat."""
        weighted = sorted((s.weighted() for s in self.get_scores(heat_id, surfer_id)),
                          reverse=True)
        return round(sum(weighted[:2]), 2)

    def surfer_result(self, heat_id, surfer):
        """Everything the ranking and the screens need about one surfer's heat."""
        scores = self.get_scores(heat_id, surfer.id)
        weighted = [s.weighted() for s in scores]
        result = surfer.as_dict()
        result["scores"] = [s.as_dict() for s in scores]
        result["total"] = round(sum(sorted(weighted, reverse=True)[:2]), 2)
        result["best_wave"] = max(weighted) if weighted else 0.0
        result["wave_count"] = len(weighted)
        return result

    # ---- Algorithm 3 ----------------------------------------------------

    def rank(self, results):
        """Rank by heat total, then best single wave, then fewest waves ridden."""
        return sorted(results,
                      key=lambda r: (-r["total"], -r["best_wave"], r["wave_count"]))

    def heat_results(self, heat_id):
        """The surfers in a heat, ranked, with their scores and totals."""
        heat = heat_manager.get_heat(heat_id)
        if heat is None:
            return None
        results = [self.surfer_result(heat_id, s) for s in heat.surfers]
        ranked = self.rank(results)
        for place, result in enumerate(ranked, start=1):
            result["place"] = place
        return {"heat": heat.as_dict(), "results": ranked}

    def advance(self, round_number, top_n):
        """Send the top N of every heat in this round into a new drawn round."""
        heats = heat_manager.get_heats(round_number)
        if not heats:
            raise ValueError("Round %d has not been drawn yet." % round_number)
        if not 1 <= top_n < 4:
            raise ValueError("The progression rule must advance 1 to 3 surfers per heat.")

        moving_on = []
        for heat in heats:
            ranked = self.rank([self.surfer_result(heat.id, s) for s in heat.surfers])
            for result in ranked[:top_n]:
                moving_on.append(next(s for s in heat.surfers if s.id == result["id"]))

        next_round = round_number + 1
        drawn = heat_manager.draw(moving_on)
        return heat_manager.save_round(next_round, drawn)

    # ---- Leaderboard ----------------------------------------------------

    def leaderboard(self):
        """Every surfer ranked by the totals they have scored across all heats."""
        results = []
        for surfer in heat_manager.get_surfers():
            heats = database.query(
                "SELECT DISTINCT heat_id FROM heat_surfers WHERE surfer_id = ?", (surfer.id,))
            row = surfer.as_dict()
            row["total"] = round(sum(self.heat_total(h["heat_id"], surfer.id)
                                     for h in heats), 2)
            all_waves = []
            for heat in heats:
                all_waves += [s.weighted() for s in self.get_scores(heat["heat_id"], surfer.id)]
            row["best_wave"] = max(all_waves) if all_waves else 0.0
            row["wave_count"] = len(all_waves)
            row["heats_surfed"] = len(heats)
            results.append(row)

        ranked = self.rank(results)
        for place, result in enumerate(ranked, start=1):
            result["place"] = place
        return ranked


score_manager = ScoreManager()
