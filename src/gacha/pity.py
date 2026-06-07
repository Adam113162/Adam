"""Pity system for guaranteed pulls."""

from dataclasses import dataclass, field

from gacha.models import Rarity


@dataclass
class PityCounter:
    """Tracks pull count and guarantees high-rarity drops."""

    soft_pity_threshold: int = 75
    hard_pity_threshold: int = 90
    epic_pity_threshold: int = 10
    _pull_count: int = field(default=0, init=False)
    _epic_pull_count: int = field(default=0, init=False)

    @property
    def pull_count(self) -> int:
        """Current number of pulls since last legendary."""
        return self._pull_count

    @property
    def epic_pull_count(self) -> int:
        """Current number of pulls since last epic or better."""
        return self._epic_pull_count

    def increment(self) -> None:
        """Increment pull counters."""
        self._pull_count += 1
        self._epic_pull_count += 1

    def reset_legendary(self) -> None:
        """Reset counter after pulling a legendary."""
        self._pull_count = 0
        self._epic_pull_count = 0

    def reset_epic(self) -> None:
        """Reset epic counter after pulling an epic."""
        self._epic_pull_count = 0

    @property
    def in_soft_pity(self) -> bool:
        """Whether the player is in soft pity range."""
        return self._pull_count >= self.soft_pity_threshold

    @property
    def at_hard_pity(self) -> bool:
        """Whether the player has hit hard pity (guaranteed legendary)."""
        return self._pull_count >= self.hard_pity_threshold

    @property
    def at_epic_pity(self) -> bool:
        """Whether the player is guaranteed an epic."""
        return self._epic_pull_count >= self.epic_pity_threshold

    def get_legendary_boost(self) -> float:
        """Calculate the legendary rate boost during soft pity."""
        if not self.in_soft_pity:
            return 0.0
        pulls_into_soft = self._pull_count - self.soft_pity_threshold
        max_pulls_in_soft = self.hard_pity_threshold - self.soft_pity_threshold
        return min(pulls_into_soft / max_pulls_in_soft, 1.0)

    def get_effective_rates(self, base_rates: dict[Rarity, float]) -> dict[Rarity, float]:
        """Calculate effective pull rates considering pity."""
        rates = dict(base_rates)

        if self.at_hard_pity:
            return {
                Rarity.COMMON: 0.0,
                Rarity.RARE: 0.0,
                Rarity.EPIC: 0.0,
                Rarity.LEGENDARY: 1.0,
            }

        if self.at_epic_pity:
            stolen = rates[Rarity.COMMON] * 0.5
            rates[Rarity.COMMON] -= stolen
            rates[Rarity.EPIC] += stolen

        if self.in_soft_pity:
            boost = self.get_legendary_boost()
            legendary_bonus = boost * 0.45
            rates[Rarity.LEGENDARY] += legendary_bonus
            rates[Rarity.COMMON] -= legendary_bonus

        # Clamp to [0, 1]
        for rarity in rates:
            rates[rarity] = max(0.0, min(1.0, rates[rarity]))

        return rates
