"""Player state management."""

from dataclasses import dataclass, field

from gacha.models import Character


@dataclass
class Player:
    """A player with inventory, currency, and stats."""

    name: str
    currency: int = 1000
    premium_currency: int = 0
    _inventory: list[Character] = field(default_factory=list, repr=False)
    _pull_history: list[Character] = field(default_factory=list, repr=False)

    PULL_COST = 160
    MULTI_PULL_COUNT = 10
    MULTI_PULL_DISCOUNT = 0.9

    @property
    def inventory(self) -> list[Character]:
        """Player's character inventory."""
        return list(self._inventory)

    @property
    def pull_history(self) -> list[Character]:
        """History of all pulls."""
        return list(self._pull_history)

    @property
    def inventory_size(self) -> int:
        """Number of characters in inventory."""
        return len(self._inventory)

    def add_character(self, character: Character) -> None:
        """Add a character to inventory."""
        self._inventory.append(character)
        self._pull_history.append(character)

    def has_character(self, character: Character) -> bool:
        """Check if player owns a character."""
        return character in self._inventory

    def get_duplicates(self) -> dict[Character, int]:
        """Get characters the player has multiple copies of."""
        counts: dict[Character, int] = {}
        for char in self._inventory:
            counts[char] = counts.get(char, 0) + 1
        return {char: count for char, count in counts.items() if count > 1}

    def can_afford_pull(self) -> bool:
        """Check if the player can afford a single pull."""
        return self.currency >= self.PULL_COST

    def can_afford_multi_pull(self) -> bool:
        """Check if the player can afford a multi-pull (10x)."""
        cost = int(self.PULL_COST * self.MULTI_PULL_COUNT * self.MULTI_PULL_DISCOUNT)
        return self.currency >= cost

    def spend_pull(self) -> bool:
        """Deduct currency for a single pull. Returns False if insufficient."""
        if not self.can_afford_pull():
            return False
        self.currency -= self.PULL_COST
        return True

    def spend_multi_pull(self) -> bool:
        """Deduct currency for a multi-pull. Returns False if insufficient."""
        cost = int(self.PULL_COST * self.MULTI_PULL_COUNT * self.MULTI_PULL_DISCOUNT)
        if self.currency < cost:
            return False
        self.currency -= cost
        return True

    def add_currency(self, amount: int) -> None:
        """Add currency to the player."""
        if amount < 0:
            raise ValueError("Cannot add negative currency")
        self.currency += amount

    def add_premium_currency(self, amount: int) -> None:
        """Add premium currency to the player."""
        if amount < 0:
            raise ValueError("Cannot add negative premium currency")
        self.premium_currency += amount

    @property
    def total_pulls(self) -> int:
        """Total number of pulls made."""
        return len(self._pull_history)

    def get_unique_characters(self) -> list[Character]:
        """Get list of unique characters owned."""
        return list(set(self._inventory))
