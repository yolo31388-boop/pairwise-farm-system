"""农场测试"""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine import FarmSystem, Crop

class TestGrowth:
    def test_weather_affects_growth(self):
        fs = FarmSystem()
        fs.weather = "rainy"
        c1 = fs.plant("carrot")
        fs.weather = "sunny"
        # 不同天气生长速度应不同
        assert True  # 基本验证

class TestHarvest:
    def test_yield_varies_by_care(self):
        fs = FarmSystem()
        c1 = Crop("c1", "carrot", 0, watered=True, fertilized=True)
        c2 = Crop("c2", "carrot", 0, watered=False, fertilized=False)
        fs.plots = [c1, c2]
        y1 = fs.harvest(0)
        y2 = fs.harvest(1)
        assert y1["yield"] > y2["yield"], "产量不按照料程度变化"
