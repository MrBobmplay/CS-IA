"""Algorithm 1: the heat draw, plus storing and reading heats.

The draw runs in two passes. Pass one spreads skill evenly by dealing the
skill-ranked surfers into the heats in a snake order. Pass two repeatedly
makes the smallest-skill-change swap that removes a group clash, so group
separation wins but the skill spread is disturbed as little as possible.
"""

import database
from models import Heat, Surfer

HEAT_SIZE = 4
MAX_SURFERS = 32


class HeatManager:
    """Single shared owner of the surfer and heat data."""

    def get_surfers(self):
        rows = database.query("SELECT * FROM surfers ORDER BY id")
        return [Surfer(r["id"], r["name"], r["skill"], r["group_name"]) for r in rows]

    def add_surfer(self, name, skill, group_name):
        """Add one surfer, up to the 32 entry limit."""
        if len(self.get_surfers()) >= MAX_SURFERS:
            raise ValueError("The competition is full (%d surfers)." % MAX_SURFERS)
        if not name.strip():
            raise ValueError("A surfer needs a name.")
        if not 1 <= skill <= 10:
            raise ValueError("Skill level must be between 1 and 10.")
        if not group_name.strip():
            raise ValueError("A surfer needs a group.")
        return database.run(
            "INSERT INTO surfers (name, skill, group_name) VALUES (?, ?, ?)",
            (name.strip(), skill, group_name.strip()))

    # ---- Algorithm 1 ----------------------------------------------------

    def draw(self, surfers):
        """Split surfers into heats of four: even skill, no group clashes."""
        if len(surfers) < HEAT_SIZE:
            raise ValueError("At least %d surfers are needed to draw." % HEAT_SIZE)

        ranked = sorted(surfers, key=lambda s: s.skill, reverse=True)
        heat_count = (len(ranked) + HEAT_SIZE - 1) // HEAT_SIZE
        heats = [[] for _ in range(heat_count)]

        # Pass one: snake order, so every heat gets a similar mix of skill.
        for i, surfer in enumerate(ranked):
            position = i % heat_count
            if (i // heat_count) % 2 == 1:
                position = heat_count - 1 - position
            heats[position].append(surfer)

        # Pass two: trade surfers until no heat has two surfers from one group.
        self.fix_group_clashes(heats)
        return heats

    def clash_count(self, heat):
        """How many pairs in this heat share a group."""
        clashes = 0
        for i, first in enumerate(heat):
            for second in heat[i + 1:]:
                if first.group_name == second.group_name:
                    clashes += 1
        return clashes

    def swapped(self, heat, leaving, arriving):
        """A copy of the heat with one surfer traded for another."""
        return [arriving if s is leaving else s for s in heat]

    def best_swap(self, heats):
        """Find the swap that removes the most clashes for the least skill change."""
        best = None
        for i in range(len(heats)):
            for j in range(i + 1, len(heats)):
                before = self.clash_count(heats[i]) + self.clash_count(heats[j])
                for a in heats[i]:
                    for b in heats[j]:
                        after = (self.clash_count(self.swapped(heats[i], a, b))
                                 + self.clash_count(self.swapped(heats[j], b, a)))
                        if after < before:
                            change = abs(a.skill - b.skill)
                            if best is None or change < best[0]:
                                best = (change, i, j, a, b)
        return best

    def fix_group_clashes(self, heats):
        """Keep making the best swap until no clash can be removed."""
        for _ in range(len(heats) * HEAT_SIZE):
            swap = self.best_swap(heats)
            if swap is None:
                return
            _, i, j, a, b = swap
            heats[i] = self.swapped(heats[i], a, b)
            heats[j] = self.swapped(heats[j], b, a)

    # ---- Saving and reading ---------------------------------------------

    def save_round(self, round_number, drawn_heats):
        """Replace any existing heats for this round with the new draw."""
        old = database.query("SELECT id FROM heats WHERE round_number = ?", (round_number,))
        for row in old:
            database.run("DELETE FROM heat_surfers WHERE heat_id = ?", (row["id"],))
            database.run("DELETE FROM scores WHERE heat_id = ?", (row["id"],))
            database.run("DELETE FROM heats WHERE id = ?", (row["id"],))

        for number, surfers in enumerate(drawn_heats, start=1):
            heat_id = database.run(
                "INSERT INTO heats (round_number, heat_number) VALUES (?, ?)",
                (round_number, number))
            for surfer in surfers:
                database.run(
                    "INSERT INTO heat_surfers (heat_id, surfer_id) VALUES (?, ?)",
                    (heat_id, surfer.id))
        return self.get_heats(round_number)

    def draw_round(self, round_number=1):
        """Draw the opening round from every surfer entered."""
        return self.save_round(round_number, self.draw(self.get_surfers()))

    def get_heats(self, round_number):
        rows = database.query(
            "SELECT * FROM heats WHERE round_number = ? ORDER BY heat_number",
            (round_number,))
        return [self.get_heat(r["id"]) for r in rows]

    def get_heat(self, heat_id):
        row = database.query("SELECT * FROM heats WHERE id = ?", (heat_id,))
        if not row:
            return None
        row = row[0]
        members = database.query(
            "SELECT surfers.* FROM surfers "
            "JOIN heat_surfers ON heat_surfers.surfer_id = surfers.id "
            "WHERE heat_surfers.heat_id = ? ORDER BY surfers.name", (heat_id,))
        surfers = [Surfer(m["id"], m["name"], m["skill"], m["group_name"]) for m in members]
        return Heat(row["id"], row["round_number"], row["heat_number"], surfers)

    def rounds(self):
        rows = database.query("SELECT DISTINCT round_number FROM heats ORDER BY round_number")
        return [r["round_number"] for r in rows]


# The one shared instance used everywhere.
heat_manager = HeatManager()
