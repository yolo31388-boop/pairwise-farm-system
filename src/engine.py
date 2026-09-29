"""家园种植农场 - 带6个bug"""
from dataclasses import dataclass, field

@dataclass
class Crop:
    cid: str
    name: str
    growth_time: float
    watered: bool = False
    fertilized: bool = False
    withered: bool = False

class FarmSystem:
    def __init__(self):
        self.plots: list[Crop] = []
        self.weather = "sunny"  # bug1: 不影响生长
        self.season = "spring"
        self.plot_limit = 999  # bug6: 无上限

    def plant(self, seed_id):
        crop = Crop(seed_id, seed_id, 60)
        self.plots.append(crop)
        return crop

    def water(self, plot_id):
        crop = self.plots[plot_id]
        # bug2: 浇水无效果
        crop.watered = True
        return True

    def harvest(self, plot_id):
        crop = self.plots[plot_id]
        # bug3: 固定产量
        return {"yield": 5}

    def tick(self, dt):
        for crop in self.plots:
            crop.growth_time -= dt
            # bug4: 不看缺水
            if crop.growth_time <= 0:
                crop.withered = True  # bug4: 时间到就枯

    def seed_value(self, seed_id):
        # bug5: 价格倒挂
        return 100
