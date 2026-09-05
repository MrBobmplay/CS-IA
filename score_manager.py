import database
from heat_manager import heat_manager
from models import WaveScore

MAX_WEIGHT = 1.3


def total_of(result):
    return result["total"]


def best_wave_of(result):
    return result["best_wave"]


def wave_count_of(result):
    return result["wave_count"]


class ScoreManager:
    def add_score(self, heat_id, surfer_id, raw_score, weight):
        if raw_score < 0 or raw_score > 10:
            raise ValueError("A wave score must be between 0 and 10.")
        if weight < 1.0 or weight > MAX_WEIGHT:
            raise ValueError("The difficulty weight must be between 1.0 and "
                             + str(MAX_WEIGHT) + ".")

        in_heat = database.query(
            "SELECT surfer_id FROM heat_surfers WHERE heat_id = ? AND surfer_id = ?",
            (heat_id, surfer_id))
        if len(in_heat) == 0:
            raise ValueError("That surfer is not in that heat.")

        return database.run(
            "INSERT INTO scores (heat_id, surfer_id, raw_score, weight) "
            "VALUES (?, ?, ?, ?)", (heat_id, surfer_id, raw_score, weight))

    def get_scores(self, heat_id, surfer_id):
        rows = database.query(
            "SELECT * FROM scores WHERE heat_id = ? AND surfer_id = ? ORDER BY id",
            (heat_id, surfer_id))
        scores = []
        for row in rows:
            scores.append(WaveScore(row["id"], row["heat_id"], row["surfer_id"],
                                    row["raw_score"], row["weight"]))
        return scores


    def best_two(self, weighted):
        weighted.sort(reverse=True)
        total = 0
        for score in weighted[:2]:
            total = total + score
        return round(total, 2)

    def heat_total(self, heat_id, surfer_id):
        weighted = []
        for score in self.get_scores(heat_id, surfer_id):
            weighted.append(score.weighted())
        return self.best_two(weighted)

    def surfer_result(self, heat_id, surfer):
        score_list = []
        weighted = []
        best_wave = 0.0
        for score in self.get_scores(heat_id, surfer.id):
            score_list.append(score.as_dict())
            weighted.append(score.weighted())
            if score.weighted() > best_wave:
                best_wave = score.weighted()

        result = surfer.as_dict()
        result["scores"] = score_list
        result["wave_count"] = len(weighted)
        result["best_wave"] = best_wave
        result["total"] = self.best_two(weighted)
        return result


    def rank(self, results):
        results.sort(key=wave_count_of)
        results.sort(key=best_wave_of, reverse=True)
        results.sort(key=total_of, reverse=True)

        place = 1
        for result in results:
            result["place"] = place
            place = place + 1
        return results

    def rank_heat(self, heat):
        results = []
        for surfer in heat.surfers:
            results.append(self.surfer_result(heat.id, surfer))
        return self.rank(results)

    def heat_results(self, heat_id):
        heat = heat_manager.get_heat(heat_id)
        if heat is None:
            return None
        return {"heat": heat.as_dict(), "results": self.rank_heat(heat)}

    def advance(self, round_number, top_n):
        heats = heat_manager.get_heats(round_number)
        if len(heats) == 0:
            raise ValueError("Round " + str(round_number) + " has not been drawn yet.")
        if top_n < 1 or top_n > 3:
            raise ValueError("The progression rule must advance 1 to 3 surfers per heat.")

        moving_on = []
        for heat in heats:
            ranked = self.rank_heat(heat)
            for place in range(top_n):
                if place < len(ranked):
                    for surfer in heat.surfers:
                        if surfer.id == ranked[place]["id"]:
                            moving_on.append(surfer)

        return heat_manager.save_round(round_number + 1, heat_manager.draw(moving_on))


    def leaderboard(self):
        results = []
        for surfer in heat_manager.get_surfers():
            heats = database.query(
                "SELECT DISTINCT heat_id FROM heat_surfers WHERE surfer_id = ?",
                (surfer.id,))

            total = 0
            best_wave = 0.0
            wave_count = 0
            for row in heats:
                total = total + self.heat_total(row["heat_id"], surfer.id)
                for score in self.get_scores(row["heat_id"], surfer.id):
                    wave_count = wave_count + 1
                    if score.weighted() > best_wave:
                        best_wave = score.weighted()

            result = surfer.as_dict()
            result["total"] = round(total, 2)
            result["best_wave"] = best_wave
            result["wave_count"] = wave_count
            result["heats_surfed"] = len(heats)
            results.append(result)

        return self.rank(results)


score_manager = ScoreManager()
