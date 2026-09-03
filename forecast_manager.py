"""Algorithm 4: ranking forecast time slots by how suitable they are.

Each slot is given a score from 0 to 1 for how close its wave height and its
tide level are to the ideal. The two are then combined, with wave height
counting for 60% and tide for 40%, because wave height has the larger effect
on whether heats can run safely at Peniche.
"""

import database
from models import ForecastSlot

IDEAL_WAVE_HEIGHT = 1.5    # metres
IDEAL_TIDE_LEVEL = 1.5     # metres, which is mid tide
WAVE_SPREAD = 1.5
TIDE_SPREAD = 1.5
WAVE_WEIGHT = 0.6
TIDE_WEIGHT = 0.4


def suitability_of(slot):
    """The sort key used to rank the slots."""
    return slot["suitability"]


class ForecastManager:
    """The single shared owner of the forecast slot data."""

    def add_slot(self, slot_time, wave_height, tide_level):
        """Save one candidate time slot entered by the director."""
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
        """Scores 1.0 at the ideal value and 0.0 once it is a spread away."""
        score = 1 - abs(value - ideal) / spread
        if score < 0:
            score = 0.0
        return score

    def suitability(self, wave_height, tide_level):
        """A score from 0 to 1 for running heats in this slot."""
        wave = self.closeness(wave_height, IDEAL_WAVE_HEIGHT, WAVE_SPREAD)
        tide = self.closeness(tide_level, IDEAL_TIDE_LEVEL, TIDE_SPREAD)
        return round(WAVE_WEIGHT * wave + TIDE_WEIGHT * tide, 3)

    def ranked_slots(self):
        """Every slot, best first."""
        rows = database.query("SELECT * FROM forecast_slots ORDER BY slot_time")

        slots = []
        for row in rows:
            slot_object = ForecastSlot(row["id"], row["slot_time"],
                                       row["wave_height"], row["tide_level"])
            slot = slot_object.as_dict()
            slot["suitability"] = self.suitability(row["wave_height"], row["tide_level"])
            slots.append(slot)

        slots.sort(key=suitability_of, reverse=True)

        rank = 1
        for slot in slots:
            slot["rank"] = rank
            rank = rank + 1
        return slots


# The one shared instance that the rest of the program uses.
forecast_manager = ForecastManager()
