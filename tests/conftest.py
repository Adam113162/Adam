"""Shared test fixtures."""

import pytest

from gacha.banner import Banner
from gacha.engine import GachaEngine
from gacha.models import Character, CharacterPool, Rarity
from gacha.pity import PityCounter
from gacha.player import Player


@pytest.fixture
def sample_characters() -> list[Character]:
    """Create a set of sample characters across all rarities."""
    return [
        Character("Slime", Rarity.COMMON, "Water", 10, 5, 50),
        Character("Goblin", Rarity.COMMON, "Earth", 12, 4, 45),
        Character("Wolf", Rarity.COMMON, "Wind", 14, 3, 40),
        Character("Knight", Rarity.RARE, "Fire", 25, 15, 80),
        Character("Mage", Rarity.RARE, "Water", 30, 10, 60),
        Character("Archer", Rarity.RARE, "Wind", 28, 12, 70),
        Character("Dragon", Rarity.EPIC, "Fire", 50, 30, 150),
        Character("Phoenix", Rarity.EPIC, "Fire", 55, 25, 140),
        Character("Kraken", Rarity.EPIC, "Water", 45, 35, 160),
        Character("Zeus", Rarity.LEGENDARY, "Lightning", 100, 50, 300),
        Character("Odin", Rarity.LEGENDARY, "Wind", 95, 55, 310),
    ]


@pytest.fixture
def character_pool(sample_characters: list[Character]) -> CharacterPool:
    """Create a populated character pool."""
    pool = CharacterPool()
    for char in sample_characters:
        pool.add(char)
    return pool


@pytest.fixture
def player() -> Player:
    """Create a player with default currency."""
    return Player(name="TestPlayer")


@pytest.fixture
def rich_player() -> Player:
    """Create a player with lots of currency."""
    return Player(name="RichPlayer", currency=100_000)


@pytest.fixture
def pity() -> PityCounter:
    """Create a fresh pity counter."""
    return PityCounter()


@pytest.fixture
def engine(character_pool: CharacterPool) -> GachaEngine:
    """Create a seeded gacha engine."""
    e = GachaEngine(pool=character_pool)
    e.set_seed(42)
    return e


@pytest.fixture
def banner(sample_characters: list[Character]) -> Banner:
    """Create a test banner with featured characters."""
    zeus = sample_characters[9]  # Legendary
    dragon = sample_characters[6]  # Epic
    return Banner(name="Test Banner", featured_characters=[zeus, dragon])
