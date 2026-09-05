class Surfer:

    def __init__(self, surfer_id, name, skill, group_name):
        self.id = surfer_id
        self.name = name
        self.skill = skill
        self.group_name = group_name

    def as_dict(self):
        return {"id": self.id, "name": self.name,
                "skill": self.skill, "group_name": self.group_name}


class WaveScore:
    def __init__(self, score_id, heat_id, surfer_id, raw_score, weight):
        self.id = score_id
        self.heat_id = heat_id
        self.surfer_id = surfer_id
        self.raw_score = raw_score
        self.weight = weight

    def weighted(self):
        return round(self.raw_score * self.weight, 2)

    def as_dict(self):
        return {"id": self.id, "raw_score": self.raw_score,
                "weight": self.weight, "weighted": self.weighted()}


class Heat:
    def __init__(self, heat_id, round_number, heat_number, surfers):
        self.id = heat_id
        self.round_number = round_number
        self.heat_number = heat_number
        self.surfers = surfers

    def as_dict(self):
        surfer_list = []
        for surfer in self.surfers:
            surfer_list.append(surfer.as_dict())
        return {"id": self.id, "round_number": self.round_number,
                "heat_number": self.heat_number, "surfers": surfer_list}


class ForecastSlot:
    def __init__(self, slot_id, slot_time, wave_height, tide_level):
        self.id = slot_id
        self.slot_time = slot_time
        self.wave_height = wave_height
        self.tide_level = tide_level

    def as_dict(self):
        return {"id": self.id, "slot_time": self.slot_time,
                "wave_height": self.wave_height, "tide_level": self.tide_level}
