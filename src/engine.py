"""家园种植农场系统"""
from dataclasses import dataclass, field

# 天气对生长速度的影响：晴天快、雨天慢
WEATHER_FACTOR = {"sunny": 1.2, "cloudy": 1.0, "rainy": 0.7}

# 作物当季/反季：当季生长快，反季慢
CROP_SEASONS = {
    "carrot": {"spring", "autumn"},
    "wheat": {"summer", "autumn"},
    "tomato": {"summer"},
    "cabbage": {"spring", "winter"},
}
IN_SEASON_FACTOR = 1.25
OFF_SEASON_FACTOR = 0.6

BASE_YIELD = 5
# 照料对产量的加成：浇水 / 施肥 / 除虫
CARE_BONUS = {"watered": 0.4, "fertilized": 0.4, "depested": 0.2}
NEGLECT_YIELD_FACTOR = 0.5  # 完全放养时的产量系数

# 枯萎判定阈值（多因素）
MAX_THIRST_DAYS = 3.0       # 连续缺水天数上限
MAX_HUNGER_DAYS = 5.0       # 连续缺肥天数上限
PEST_WITHER_DAYS = 2.0      # 病虫害不处理可忍受天数

# 种子目录：价格 < 产出预期价值（已扣除时间成本与风险折扣）
SEED_CATALOG = {
    "carrot": {"price": 20, "crop_value": 12, "growth_time": 60},
    "wheat": {"price": 35, "crop_value": 9, "growth_time": 90},
    "tomato": {"price": 50, "crop_value": 15, "growth_time": 120},
    "cabbage": {"price": 15, "crop_value": 8, "growth_time": 45},
}
DEFAULT_SEED = {"price": 20, "crop_value": 12, "growth_time": 60}
RISK_DISCOUNT = 0.7  # 风险与时间成本折现

# 农田上限：随家园等级解锁
BASE_PLOTS = 2
PLOTS_PER_LEVEL = 2


@dataclass
class Crop:
    cid: str
    name: str
    growth_time: float
    watered: bool = False
    fertilized: bool = False
    withered: bool = False
    depested: bool = False
    mature: bool = False
    soil_fertility: float = 1.0
    thirst_days: float = 0.0
    hunger_days: float = 0.0
    pest_days: float = 0.0
    has_pests: bool = False


class FarmSystem:
    def __init__(self, home_level: int = 1):
        self.plots: list[Crop] = []
        self.weather = "sunny"
        self.season = "spring"
        self.home_level = home_level

    @property
    def plot_limit(self):
        # bug6 修复：农田数量有上限，随家园等级解锁
        return BASE_PLOTS + self.home_level * PLOTS_PER_LEVEL

    def plant(self, seed_id):
        if len(self.plots) >= self.plot_limit:
            return None
        spec = SEED_CATALOG.get(seed_id, DEFAULT_SEED)
        crop = Crop(seed_id, seed_id, float(spec["growth_time"]))
        self.plots.append(crop)
        return crop

    def water(self, plot_id):
        crop = self.plots[plot_id]
        if crop.withered:
            return False
        # bug2 修复：浇水恢复水分，影响生长速度与产量
        crop.watered = True
        crop.thirst_days = 0.0
        return True

    def fertilize(self, plot_id):
        crop = self.plots[plot_id]
        if crop.withered:
            return False
        crop.fertilized = True
        crop.hunger_days = 0.0
        crop.soil_fertility = min(1.0, crop.soil_fertility + 0.2)
        return True

    def depest(self, plot_id):
        crop = self.plots[plot_id]
        if crop.withered:
            return False
        crop.depested = True
        crop.has_pests = False
        crop.pest_days = 0.0
        return True

    def _growth_factor(self, crop):
        weather = WEATHER_FACTOR.get(self.weather, 1.0)
        seasons = CROP_SEASONS.get(crop.name)
        if seasons is None:
            season = 1.0
        elif self.season in seasons:
            season = IN_SEASON_FACTOR
        else:
            season = OFF_SEASON_FACTOR
        fertility = 0.5 + 0.5 * crop.soil_fertility
        return weather * season * fertility

    def tick(self, dt):
        for crop in self.plots:
            if crop.withered or crop.mature:
                continue
            # bug2 修复：缺水暂停生长
            if crop.watered:
                crop.growth_time -= dt * self._growth_factor(crop)
            else:
                crop.thirst_days += dt
            if not crop.fertilized:
                crop.hunger_days += dt
            if crop.has_pests and not crop.depested:
                crop.pest_days += dt
            # 水分/养分随时间消耗
            if dt >= 1.0:
                crop.watered = False
                crop.soil_fertility = max(0.0, crop.soil_fertility - 0.05 * dt)
            # bug4 修复：枯萎由缺水、缺肥、病虫害多因素判定
            if (
                crop.thirst_days >= MAX_THIRST_DAYS
                or crop.hunger_days >= MAX_HUNGER_DAYS
                or crop.pest_days >= PEST_WITHER_DAYS
            ):
                crop.withered = True
                continue
            # 生长时间归零 = 成熟，而不是枯萎
            if crop.growth_time <= 0:
                crop.mature = True

    def harvest(self, plot_id):
        crop = self.plots[plot_id]
        if crop.withered:
            return {"yield": 0}
        # bug3 修复：产量按照料程度（浇水/施肥/除虫）浮动
        bonus = 0.0
        for key, weight in CARE_BONUS.items():
            if getattr(crop, key):
                bonus += weight
        factor = NEGLECT_YIELD_FACTOR + bonus
        return {"yield": round(BASE_YIELD * factor)}

    def seed_value(self, seed_id):
        # bug5 修复：种子价格低于产出预期价值（含时间与风险折现）
        spec = SEED_CATALOG.get(seed_id, DEFAULT_SEED)
        expected = spec["crop_value"] * BASE_YIELD * RISK_DISCOUNT
        return min(spec["price"], round(expected) - 1)
