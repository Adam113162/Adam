"""Tests for gacha.pity module."""

from gacha.models import RARITY_WEIGHTS, Rarity
from gacha.pity import PityCounter


class TestPityCounter:
    def test_initial_state(self, pity):
        assert pity.pull_count == 0
        assert pity.epic_pull_count == 0
        assert not pity.in_soft_pity
        assert not pity.at_hard_pity
        assert not pity.at_epic_pity

    def test_increment(self, pity):
        pity.increment()
        assert pity.pull_count == 1
        assert pity.epic_pull_count == 1

    def test_reset_legendary(self, pity):
        for _ in range(50):
            pity.increment()
        pity.reset_legendary()
        assert pity.pull_count == 0
        assert pity.epic_pull_count == 0

    def test_reset_epic(self, pity):
        for _ in range(5):
            pity.increment()
        pity.reset_epic()
        assert pity.epic_pull_count == 0
        assert pity.pull_count == 5  # legendary counter unchanged

    def test_soft_pity_threshold(self, pity):
        for _ in range(74):
            pity.increment()
        assert not pity.in_soft_pity
        pity.increment()  # 75th pull
        assert pity.in_soft_pity

    def test_hard_pity_threshold(self, pity):
        for _ in range(89):
            pity.increment()
        assert not pity.at_hard_pity
        pity.increment()  # 90th pull
        assert pity.at_hard_pity

    def test_epic_pity_threshold(self, pity):
        for _ in range(9):
            pity.increment()
        assert not pity.at_epic_pity
        pity.increment()  # 10th pull
        assert pity.at_epic_pity

    def test_custom_thresholds(self):
        pity = PityCounter(soft_pity_threshold=50, hard_pity_threshold=60, epic_pity_threshold=5)
        for _ in range(50):
            pity.increment()
        assert pity.in_soft_pity
        assert not pity.at_hard_pity

    def test_legendary_boost_before_soft_pity(self, pity):
        assert pity.get_legendary_boost() == 0.0

    def test_legendary_boost_at_soft_pity(self, pity):
        for _ in range(75):
            pity.increment()
        assert pity.get_legendary_boost() == 0.0  # exactly at threshold

    def test_legendary_boost_during_soft_pity(self, pity):
        for _ in range(80):
            pity.increment()
        # (80 - 75) / (90 - 75) = 5/15 ≈ 0.333
        boost = pity.get_legendary_boost()
        assert abs(boost - 5 / 15) < 1e-9

    def test_legendary_boost_capped_at_one(self, pity):
        for _ in range(100):
            pity.increment()
        assert pity.get_legendary_boost() == 1.0


class TestEffectiveRates:
    def test_no_pity_returns_base_rates(self, pity):
        rates = pity.get_effective_rates(dict(RARITY_WEIGHTS))
        assert rates == RARITY_WEIGHTS

    def test_hard_pity_guarantees_legendary(self, pity):
        for _ in range(90):
            pity.increment()
        rates = pity.get_effective_rates(dict(RARITY_WEIGHTS))
        assert rates[Rarity.LEGENDARY] == 1.0
        assert rates[Rarity.COMMON] == 0.0
        assert rates[Rarity.RARE] == 0.0
        assert rates[Rarity.EPIC] == 0.0

    def test_epic_pity_boosts_epic_rate(self, pity):
        for _ in range(10):
            pity.increment()
        rates = pity.get_effective_rates(dict(RARITY_WEIGHTS))
        assert rates[Rarity.EPIC] > RARITY_WEIGHTS[Rarity.EPIC]
        assert rates[Rarity.COMMON] < RARITY_WEIGHTS[Rarity.COMMON]

    def test_soft_pity_boosts_legendary_rate(self, pity):
        for _ in range(80):
            pity.increment()
        rates = pity.get_effective_rates(dict(RARITY_WEIGHTS))
        assert rates[Rarity.LEGENDARY] > RARITY_WEIGHTS[Rarity.LEGENDARY]

    def test_rates_stay_non_negative(self, pity):
        for _ in range(89):
            pity.increment()
        rates = pity.get_effective_rates(dict(RARITY_WEIGHTS))
        for r in rates.values():
            assert r >= 0.0
