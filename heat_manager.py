import database
from models import Heat, Surfer

HEAT_SIZE = 4
MAX_SURFERS = 32


def skill_of(surfer):
    return surfer.skill


class HeatManager:
    def get_surfers(self):
        rows = database.query("SELECT * FROM surfers ORDER BY id")
        surfers = []
        for row in rows:
            surfers.append(Surfer(row["id"], row["name"], row["skill"], row["group_name"]))
        return surfers

    def add_surfer(self, name, skill, group_name):
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


    def count_heats(self, surfer_count):
        heats = surfer_count // HEAT_SIZE
        if surfer_count % HEAT_SIZE > 0:
            heats = heats + 1
        return heats

    def draw(self, surfers):
        if len(surfers) < HEAT_SIZE:
            raise ValueError("At least " + str(HEAT_SIZE) + " surfers are needed to draw.")

        ranked = sorted(surfers, key=skill_of, reverse=True)
        heat_count = self.count_heats(len(ranked))
        heats = []
        for i in range(heat_count):
            heats.append([])

        position = 0
        step = 1
        for surfer in ranked:
            heats[position].append(surfer)
            if position + step < 0 or position + step >= heat_count:
                step = -step
            else:
                position = position + step

        self.fix_group_clashes(heats)
        return heats

    def clash_count(self, heat):
        clashes = 0
        for i in range(len(heat)):
            for j in range(i + 1, len(heat)):
                if heat[i].group_name == heat[j].group_name:
                    clashes = clashes + 1
        return clashes

    def swap(self, heats, heat_a, place_a, heat_b, place_b):
        keep = heats[heat_a][place_a]
        heats[heat_a][place_a] = heats[heat_b][place_b]
        heats[heat_b][place_b] = keep

    def best_swap(self, heats):
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
                        self.swap(heats, a, i, b, j)
                        if after < before:
                            if best_move is None or change < best_change:
                                best_move = [a, i, b, j]
                                best_change = change
        return best_move

    def fix_group_clashes(self, heats):
        move = self.best_swap(heats)
        while move is not None:
            self.swap(heats, move[0], move[1], move[2], move[3])
            move = self.best_swap(heats)


    def save_round(self, round_number, drawn_heats):
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
        return self.save_round(round_number, self.draw(self.get_surfers()))

    def get_heats(self, round_number):
        rows = database.query(
            "SELECT * FROM heats WHERE round_number = ? ORDER BY heat_number",
            (round_number,))
        heats = []
        for row in rows:
            heats.append(self.get_heat(row["id"]))
        return heats

    def get_heat(self, heat_id):
        rows = database.query("SELECT * FROM heats WHERE id = ?", (heat_id,))
        if len(rows) == 0:
            return None

        members = database.query(
            "SELECT surfers.* FROM surfers "
            "JOIN heat_surfers ON heat_surfers.surfer_id = surfers.id "
            "WHERE heat_surfers.heat_id = ? ORDER BY surfers.name", (heat_id,))
        surfers = []
        for row in members:
            surfers.append(Surfer(row["id"], row["name"], row["skill"], row["group_name"]))

        return Heat(rows[0]["id"], rows[0]["round_number"], rows[0]["heat_number"], surfers)

    def rounds(self):
        rows = database.query(
            "SELECT DISTINCT round_number FROM heats ORDER BY round_number")
        numbers = []
        for row in rows:
            numbers.append(row["round_number"])
        return numbers


heat_manager = HeatManager()
