"""家园种植农场系统"""
from dataclasses import dataclass

CROP_DATA = {
    "carrot": {"growth": 60.0, "seasons": {"spring", "autumn"}, "base_yield": 5, "unit_price": 12},
    "wheat": {"growth": 80.0, "seasons": {"summer", "autumn"}, "base_yield": 8, "unit_price": 9},
    "melon": {"growth": 100.0, "seasons": {"summer"}, "base_yield": 3, "unit_price": 30},
}
DEFAULT_CROP = {"growth": 60.0, "seasons": {"spring", "summer", "autumn", "winter"},
                "base_yield": 5, "unit_price": 10}

WEATHER_SPEED = {"sunny": 1.2, "cloudy": 1.0, "rainy": 0.7}
IN_SEASON_SPEED = 1.25
OFF_SEASON_SPEED = 0.6
FERTILIZED_SPEED = 1.2

WATER_DURATION = 3.0
FERTILIZER_DURATION = 4.0
THIRST_LIMIT = 3.0
HUNGER_LIMIT = 5.0
PEST_LIMIT = 4.0

WATER_YIELD_BONUS = 0.4
FERTILIZER_YIELD_BONUS = 0.4
PEST_YIELD_PENALTY = 0.5

RISK_MARGIN = 0.7
TIME_COST_PER_DAY = 0.5


@dataclass
class Crop:
    cid: str
    name: str
    growth_time: float
    watered: bool = False
    fertilized: bool = False
    withered: bool = False
    pests: bool = False
    water_level: float = 0.0
    fert_level: float = 0.0
    thirst_days: float = 0.0
    hunger_days: float = 0.0
    pest_days: float = 0.0

    @property
    def data(self):
        return CROP_DATA.get(self.name, DEFAULT_CROP)

    @property
    def mature(self):
        return self.growth_time <= 0


class FarmSystem:
    def __init__(self, home_level=1):
        self.home_level = home_level
        self.plots: list[Crop] = []
        self.weather = "sunny"
        self.season = "spring"
        self.soil_fertility = 1.0
        self.plot_limit = 1 + home_level

    def plant(self, seed_id):
        if len(self.plots) >= self.plot_limit:
            return None
        data = CROP_DATA.get(seed_id, DEFAULT_CROP)
        crop = Crop(seed_id, seed_id, data["growth"])
        self.plots.append(crop)
        return crop

    def water(self, plot_id):
        crop = self.plots[plot_id]
        crop.watered = True
        crop.water_level = WATER_DURATION
        crop.thirst_days = 0.0
        return True

    def fertilize(self, plot_id):
        crop = self.plots[plot_id]
        crop.fertilized = True
        crop.fert_level = FERTILIZER_DURATION
        crop.hunger_days = 0.0
        return True

    def remove_pests(self, plot_id):
        crop = self.plots[plot_id]
        crop.pests = False
        crop.pest_days = 0.0
        return True

    def growth_speed(self, crop):
        speed = WEATHER_SPEED.get(self.weather, 1.0)
        speed *= IN_SEASON_SPEED if self.season in crop.data["seasons"] else OFF_SEASON_SPEED
        speed *= 0.5 + 0.5 * self.soil_fertility
        if crop.fertilized:
            speed *= FERTILIZED_SPEED
        return speed

    def tick(self, dt):
        for crop in self.plots:
            if crop.withered or crop.mature:
                continue
            if crop.water_level > 0:
                crop.water_level = max(0.0, crop.water_level - dt)
                crop.watered = crop.water_level > 0
                crop.growth_time = max(0.0, crop.growth_time - dt * self.growth_speed(crop))
            else:
                crop.watered = False
                crop.thirst_days += dt
            if crop.fert_level > 0:
                crop.fert_level = max(0.0, crop.fert_level - dt)
                crop.fertilized = crop.fert_level > 0
            else:
                crop.fertilized = False
                crop.hunger_days += dt
            if crop.pests:
                crop.pest_days += dt
            if (crop.thirst_days >= THIRST_LIMIT
                    or crop.hunger_days >= HUNGER_LIMIT
                    or crop.pest_days >= PEST_LIMIT):
                crop.withered = True

    def care_level(self, crop):
        level = 1.0
        if crop.watered:
            level += WATER_YIELD_BONUS
        if crop.fertilized:
            level += FERTILIZER_YIELD_BONUS
        if crop.pests:
            level -= PEST_YIELD_PENALTY
        return max(level, 0.1)

    def harvest(self, plot_id):
        crop = self.plots[plot_id]
        if crop.withered:
            return {"yield": 0}
        return {"yield": max(1, round(crop.data["base_yield"] * self.care_level(crop)))}

    def seed_price(self, seed_id):
        data = CROP_DATA.get(seed_id, DEFAULT_CROP)
        expected_revenue = data["base_yield"] * data["unit_price"]
        time_cost = data["growth"] * TIME_COST_PER_DAY
        return max(1, round(expected_revenue * RISK_MARGIN - time_cost))

    def seed_value(self, seed_id):
        return self.seed_price(seed_id)
