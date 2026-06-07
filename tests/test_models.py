"""Tests for gacha.models module."""

import pytest

from gacha.models import RARITY_WEIGHTS, Character, CharacterPool, Rarity


class TestRarity:
    def test_rarity_values(self):
        assert Rarity.COMMON.value == "common"
        assert Rarity.RARE.value == "rare"
        assert Rarity.EPIC.value == "epic"
        assert Rarity.LEGENDARY.value == "legendary"

    def test_rarity_weights_sum_to_one(self):
        total = sum(RARITY_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9

    def test_all_rarities_have_weights(self):
        for rarity in Rarity:
            assert rarity in RARITY_WEIGHTS


class TestCharacter:
    def test_creation(self):
        char = Character("Hero", Rarity.RARE, "Fire", 25, 15, 80)
        assert char.name == "Hero"
        assert char.rarity == Rarity.RARE
        assert char.element == "Fire"
        assert char.attack == 25
        assert char.defense == 15
        assert char.hp == 80

    def test_power_rating(self):
        char = Character("Hero", Rarity.RARE, "Fire", 25, 15, 80)
        # attack*2 + defense + hp = 50 + 15 + 80 = 145
        assert char.power_rating == 145

    def test_rarity_multiplier_common(self):
        char = Character("Slime", Rarity.COMMON, "Water", 10, 5, 50)
        assert char.rarity_multiplier == 1.0

    def test_rarity_multiplier_rare(self):
        char = Character("Knight", Rarity.RARE, "Fire", 25, 15, 80)
        assert char.rarity_multiplier == 1.5

    def test_rarity_multiplier_epic(self):
        char = Character("Dragon", Rarity.EPIC, "Fire", 50, 30, 150)
        assert char.rarity_multiplier == 2.0

    def test_rarity_multiplier_legendary(self):
        char = Character("Zeus", Rarity.LEGENDARY, "Lightning", 100, 50, 300)
        assert char.rarity_multiplier == 3.0

    def test_effective_power(self):
        char = Character("Knight", Rarity.RARE, "Fire", 25, 15, 80)
        expected = (25 * 2 + 15 + 80) * 1.5
        assert char.effective_power == expected

    def test_frozen_immutable(self):
        char = Character("Hero", Rarity.RARE, "Fire", 25, 15, 80)
        with pytest.raises(Exception):
            char.name = "Villain"  # type: ignore[misc]

    def test_equality(self):
        c1 = Character("Hero", Rarity.RARE, "Fire", 25, 15, 80)
        c2 = Character("Hero", Rarity.RARE, "Fire", 25, 15, 80)
        assert c1 == c2

    def test_hashable(self):
        char = Character("Hero", Rarity.RARE, "Fire", 25, 15, 80)
        s = {char}
        assert char in s


class TestCharacterPool:
    def test_empty_pool(self):
        pool = CharacterPool()
        assert pool.size == 0

    def test_add_character(self, sample_characters):
        pool = CharacterPool()
        pool.add(sample_characters[0])
        assert pool.size == 1

    def test_get_by_rarity(self, character_pool):
        commons = character_pool.get_by_rarity(Rarity.COMMON)
        assert len(commons) == 3
        assert all(c.rarity == Rarity.COMMON for c in commons)

    def test_get_by_rarity_legendary(self, character_pool):
        legends = character_pool.get_by_rarity(Rarity.LEGENDARY)
        assert len(legends) == 2

    def test_get_by_element(self, character_pool):
        fire_chars = character_pool.get_by_element("Fire")
        assert len(fire_chars) == 3
        assert all(c.element == "Fire" for c in fire_chars)

    def test_get_by_element_not_found(self, character_pool):
        result = character_pool.get_by_element("Dark")
        assert result == []

    def test_get_by_name_found(self, character_pool):
        char = character_pool.get_by_name("Zeus")
        assert char is not None
        assert char.name == "Zeus"
        assert char.rarity == Rarity.LEGENDARY

    def test_get_by_name_not_found(self, character_pool):
        assert character_pool.get_by_name("NotACharacter") is None

    def test_size(self, character_pool):
        assert character_pool.size == 11
