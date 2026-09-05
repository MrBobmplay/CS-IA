import database
from models import ForecastSlot

IDEAL_WAVE_HEIGHT = 1.5
IDEAL_TIDE_LEVEL = 1.5
WAVE_SPREAD = 1.5
TIDE_SPREAD = 1.5
WAVE_WEIGHT = 0.6
TIDE_WEIGHT = 0.4


def suitability_of(slot):
    return slot["suitability"]


class ForecastManager:
    def add_slot(self, slot_time, wave_height, tide_level):
        if slot_time.strip() == "":
            raise ValueError("A slot needs a time.")
        if wave_height < 0 or wave_height > 6:
            raise ValueError("Wave height must be between 0 and 6 metres.")
        if tide_level < 0 or tide_level > 4:
            raise ValueError("Tide level must be between 0 and 4 metres.")
        return database.run(
            "INSERT INTO forecast_slots (slot_time, wave_height, tide_level) "
            "VALUES (?, ?, ?)", (slot_time.strip(), wave_height, tide_level))

    def closeness(self, value, ideal, spread):
        score = 1 - abs(value - ideal) / spread
        if score < 0:
            score = 0.0
        return score

    def suitability(self, wave_height, tide_level):
        wave = self.closeness(wave_height, IDEAL_WAVE_HEIGHT, WAVE_SPREAD)
        tide = self.closeness(tide_level, IDEAL_TIDE_LEVEL, TIDE_SPREAD)
        return round(WAVE_WEIGHT * wave + TIDE_WEIGHT * tide, 3)

    def ranked_slots(self):
        rows = database.query("SELECT * FROM forecast_slots ORDER BY slot_time")
        slots = []
        for row in rows:
            slot = ForecastSlot(row["id"], row["slot_time"],
                                row["wave_height"], row["tide_level"]).as_dict()
            slot["suitability"] = self.suitability(row["wave_height"], row["tide_level"])
            slots.append(slot)

        slots.sort(key=suitability_of, reverse=True)
        rank = 1
        for slot in slots:
            slot["rank"] = rank
            rank = rank + 1
        return slots


forecast_manager = ForecastManager()
