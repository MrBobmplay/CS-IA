"""Algorithm 4: ranking forecast time slots by how suitable they are.

Each slot is scored 0-1 on how close its wave height and tide level are to
the ideal, then the two are combined 60% wave height to 40% tide, because
wave height matters more for whether heats can run safely at Peniche.
"""

import database
from models import ForecastSlot

IDEAL_WAVE_HEIGHT = 1.5   # metres
IDEAL_TIDE_LEVEL = 1.5    # metres, mid tide
WAVE_SPREAD = 1.5
TIDE_SPREAD = 1.5
WAVE_WEIGHT = 0.6
TIDE_WEIGHT = 0.4


class ForecastManager:
    """Single shared owner of the forecast slot data."""

    def add_slot(self, slot_time, wave_height, tide_level):
        if not slot_time.strip():
            raise ValueError("A slot needs a time.")
        if not 0 <= wave_height <= 6:
            raise ValueError("Wave height must be between 0 and 6 metres.")
        if not 0 <= tide_level <= 4:
            raise ValueError("Tide level must be between 0 and 4 metres.")
        return database.run(
            "INSERT INTO forecast_slots (slot_time, wave_height, tide_level) VALUES (?, ?, ?)",
            (slot_time.strip(), wave_height, tide_level))

    def closeness(self, value, ideal, spread):
        """1.0 at the ideal value, falling to 0.0 once it is a spread away."""
        return max(0.0, 1 - abs(value - ideal) / spread)

    def suitability(self, wave_height, tide_level):
        """A 0-1 score for running heats in this slot."""
        wave = self.closeness(wave_height, IDEAL_WAVE_HEIGHT, WAVE_SPREAD)
        tide = self.closeness(tide_level, IDEAL_TIDE_LEVEL, TIDE_SPREAD)
        return round(WAVE_WEIGHT * wave + TIDE_WEIGHT * tide, 3)

    def ranked_slots(self):
        """Every slot, best first."""
        rows = database.query("SELECT * FROM forecast_slots ORDER BY slot_time")
        slots = []
        for row in rows:
            slot = ForecastSlot(row["id"], row["slot_time"],
                                row["wave_height"], row["tide_level"]).as_dict()
            slot["suitability"] = self.suitability(row["wave_height"], row["tide_level"])
            slots.append(slot)

        slots.sort(key=lambda s: -s["suitability"])
        for rank, slot in enumerate(slots, start=1):
            slot["rank"] = rank
        return slots


forecast_manager = ForecastManager()
