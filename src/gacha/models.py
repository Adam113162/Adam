"""Data models for the gacha game."""

from dataclasses import dataclass, field
from enum import Enum


class Rarity(Enum):
    """Character rarity tiers."""

    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


RARITY_WEIGHTS: dict[Rarity, float] = {
    Rarity.COMMON: 0.60,
    Rarity.RARE: 0.25,
    Rarity.EPIC: 0.10,
    Rarity.LEGENDARY: 0.05,
}


@dataclass(frozen=True)
class Character:
    """A gacha character."""

    name: str
    rarity: Rarity
    element: str
    attack: int
    defense: int
    hp: int

    @property
    def power_rating(self) -> int:
        """Calculate overall power rating."""
        return self.attack * 2 + self.defense + self.hp

    @property
    def rarity_multiplier(self) -> float:
        """Multiplier based on rarity tier."""
        multipliers = {
            Rarity.COMMON: 1.0,
            Rarity.RARE: 1.5,
            Rarity.EPIC: 2.0,
            Rarity.LEGENDARY: 3.0,
        }
        return multipliers[self.rarity]

    @property
    def effective_power(self) -> float:
        """Power rating scaled by rarity."""
        return self.power_rating * self.rarity_multiplier


@dataclass
class CharacterPool:
    """A pool of characters organized by rarity."""

    characters: list[Character] = field(default_factory=list)

    def add(self, character: Character) -> None:
        """Add a character to the pool."""
        self.characters.append(character)

    def get_by_rarity(self, rarity: Rarity) -> list[Character]:
        """Get all characters of a specific rarity."""
        return [c for c in self.characters if c.rarity == rarity]

    def get_by_element(self, element: str) -> list[Character]:
        """Get all characters of a specific element."""
        return [c for c in self.characters if c.element == element]

    def get_by_name(self, name: str) -> Character | None:
        """Find a character by name."""
        for c in self.characters:
            if c.name == name:
                return c
        return None

    @property
    def size(self) -> int:
        """Total number of characters in the pool."""
        return len(self.characters)
