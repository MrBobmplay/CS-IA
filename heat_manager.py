"""Algorithm 1: the heat draw, plus saving and reading heats.

The draw works in two passes. Pass one deals the surfers out in skill order
so every heat gets a similar mix of skill. Pass two swaps surfers between
heats until no heat has two surfers from the same group, always choosing the
swap with the smallest change in skill so pass one is disturbed as little as
possible.
"""

import database
from models import Heat
from models import Surfer

HEAT_SIZE = 4
MAX_SURFERS = 32


def skill_of(surfer):
    """The sort key used to rank surfers by skill."""
    return surfer.skill


class HeatManager:
    """The single shared owner of the surfer and heat data."""

    # ---- Surfers (SC1, SC2) ---------------------------------------------

    def get_surfers(self):
        """Every surfer entered in the competition."""
        rows = database.query("SELECT * FROM surfers ORDER BY id")
        surfers = []
        for row in rows:
            surfer = Surfer(row["id"], row["name"], row["skill"], row["group_name"])
            surfers.append(surfer)
        return surfers

    def add_surfer(self, name, skill, group_name):
        """Add one surfer, up to the limit of 32."""
        if len(self.get_surfers()) >= MAX_SURFERS:
            raise ValueError("The competition is full (" + str(MAX_SURFERS) + " surfers).")
        if name.strip() == "":
            raise ValueError("A surfer needs a name.")
        if skill < 1 or skill > 10:
            raise ValueError("Skill level must be between 1 and 10.")
        if group_name.strip() == "":
            raise ValueError("A surfer needs a group.")

        return database.run(
            "INSERT INTO surfers (name, skill, group_name) VALUES (?, ?, ?)",
            (name.strip(), skill, group_name.strip()))

    # ---- Algorithm 1 (SC3, SC4, SC5) ------------------------------------

    def count_heats(self, surfer_count):
        """How many heats of four are needed for this many surfers."""
        heats = surfer_count // HEAT_SIZE
        if surfer_count % HEAT_SIZE > 0:
            heats = heats + 1
        return heats

    def draw(self, surfers):
        """Split the surfers into heats: even skill, no group clashes."""
        if len(surfers) < HEAT_SIZE:
            raise ValueError("At least " + str(HEAT_SIZE) + " surfers are needed to draw.")

        ranked = sorted(surfers, key=skill_of, reverse=True)
        heat_count = self.count_heats(len(ranked))

        heats = []
        for i in range(heat_count):
            heats.append([])

        # Pass one: deal the ranked surfers along the heats and back again,
        # like a snake, so the strongest surfers end up spread out.
        position = 0
        step = 1
        for surfer in ranked:
            heats[position].append(surfer)
            if position + step < 0 or position + step >= heat_count:
                step = -step          # turn around at the end of the row
            else:
                position = position + step

        # Pass two: trade surfers until the groups are separated.
        self.fix_group_clashes(heats)
        return heats

    def clash_count(self, heat):
        """How many pairs in this heat come from the same group."""
        clashes = 0
        for i in range(len(heat)):
            for j in range(i + 1, len(heat)):
                if heat[i].group_name == heat[j].group_name:
                    clashes = clashes + 1
        return clashes

    def swap(self, heats, heat_a, place_a, heat_b, place_b):
        """Trade the surfer in one heat place for the surfer in another."""
        keep = heats[heat_a][place_a]
        heats[heat_a][place_a] = heats[heat_b][place_b]
        heats[heat_b][place_b] = keep

    def best_swap(self, heats):
        """Try every possible swap and keep the best one.

        A swap is only allowed if it lowers the number of group clashes.
        Out of those, the best one is the swap between the two surfers whose
        skill levels are closest. Returns None when no swap helps.
        """
        best_move = None
        best_change = 0

        for a in range(len(heats)):
            for b in range(a + 1, len(heats)):
                before = self.clash_count(heats[a]) + self.clash_count(heats[b])

                for i in range(len(heats[a])):
                    for j in range(len(heats[b])):
                        change = abs(heats[a][i].skill - heats[b][j].skill)

                        self.swap(heats, a, i, b, j)
                        after = self.clash_count(heats[a]) + self.clash_count(heats[b])
                        self.swap(heats, a, i, b, j)      # put them back again

                        if after < before:
                            if best_move is None or change < best_change:
                                best_move = [a, i, b, j]
                                best_change = change

        return best_move

    def fix_group_clashes(self, heats):
        """Keep making the best swap until no swap removes a clash.

        Every swap made here lowers the total number of clashes by at least
        one, so the loop always ends.
        """
        move = self.best_swap(heats)
        while move is not None:
            self.swap(heats, move[0], move[1], move[2], move[3])
            move = self.best_swap(heats)

    # ---- Saving and reading heats ---------------------------------------

    def save_round(self, round_number, drawn_heats):
        """Replace any heats already saved for this round with the new draw."""
        old_heats = database.query(
            "SELECT id FROM heats WHERE round_number = ?", (round_number,))
        for row in old_heats:
            database.run("DELETE FROM heat_surfers WHERE heat_id = ?", (row["id"],))
            database.run("DELETE FROM scores WHERE heat_id = ?", (row["id"],))
            database.run("DELETE FROM heats WHERE id = ?", (row["id"],))

        heat_number = 1
        for surfers in drawn_heats:
            heat_id = database.run(
                "INSERT INTO heats (round_number, heat_number) VALUES (?, ?)",
                (round_number, heat_number))
            for surfer in surfers:
                database.run(
                    "INSERT INTO heat_surfers (heat_id, surfer_id) VALUES (?, ?)",
                    (heat_id, surfer.id))
            heat_number = heat_number + 1

        return self.get_heats(round_number)

    def draw_round(self, round_number):
        """Draw a round using every surfer entered."""
        drawn_heats = self.draw(self.get_surfers())
        return self.save_round(round_number, drawn_heats)

    def get_heats(self, round_number):
        """Every heat in one round."""
        rows = database.query(
            "SELECT * FROM heats WHERE round_number = ? ORDER BY heat_number",
            (round_number,))
        heats = []
        for row in rows:
            heats.append(self.get_heat(row["id"]))
        return heats

    def get_heat(self, heat_id):
        """One heat and the surfers in it, or None if it does not exist."""
        rows = database.query("SELECT * FROM heats WHERE id = ?", (heat_id,))
        if len(rows) == 0:
            return None
        heat_row = rows[0]

        members = database.query(
            "SELECT surfers.* FROM surfers "
            "JOIN heat_surfers ON heat_surfers.surfer_id = surfers.id "
            "WHERE heat_surfers.heat_id = ? ORDER BY surfers.name", (heat_id,))

        surfers = []
        for row in members:
            surfers.append(Surfer(row["id"], row["name"], row["skill"], row["group_name"]))

        return Heat(heat_row["id"], heat_row["round_number"],
                    heat_row["heat_number"], surfers)

    def rounds(self):
        """The round numbers that have been drawn so far."""
        rows = database.query(
            "SELECT DISTINCT round_number FROM heats ORDER BY round_number")
        numbers = []
        for row in rows:
            numbers.append(row["round_number"])
        return numbers


# The one shared instance that the rest of the program uses.
heat_manager = HeatManager()
