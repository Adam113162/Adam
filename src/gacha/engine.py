"""Core gacha engine - the pull/summon system."""

import random
from dataclasses import dataclass, field

from gacha.banner import Banner
from gacha.models import RARITY_WEIGHTS, Character, CharacterPool, Rarity
from gacha.pity import PityCounter
from gacha.player import Player


@dataclass
class PullResult:
    """Result of a gacha pull."""

    character: Character
    is_new: bool
    is_featured: bool
    is_pity: bool


@dataclass
class GachaEngine:
    """The core gacha pull engine."""

    pool: CharacterPool
    base_rates: dict[Rarity, float] = field(default_factory=lambda: dict(RARITY_WEIGHTS))
    _rng: random.Random = field(default_factory=random.Random)

    def set_seed(self, seed: int) -> None:
        """Set RNG seed for reproducible pulls."""
        self._rng = random.Random(seed)

    def _select_rarity(self, rates: dict[Rarity, float]) -> Rarity:
        """Select a rarity tier based on rates."""
        rarities = list(rates.keys())
        weights = [rates[r] for r in rarities]
        return self._rng.choices(rarities, weights=weights, k=1)[0]

    def _select_character(
        self, rarity: Rarity, banner: Banner | None = None
    ) -> Character:
        """Select a character of the given rarity, considering banner rate-ups."""
        candidates = self.pool.get_by_rarity(rarity)
        if not candidates:
            all_chars = self.pool.characters
            if not all_chars:
                raise ValueError("Character pool is empty")
            return self._rng.choice(all_chars)

        if banner and banner.is_active:
            featured = banner.get_featured_by_rarity(rarity)
            if featured:
                # 50% chance to get a featured character
                if self._rng.random() < 0.5:
                    return self._rng.choice(featured)

        return self._rng.choice(candidates)

    def pull(
        self,
        player: Player,
        pity: PityCounter,
        banner: Banner | None = None,
    ) -> PullResult | None:
        """Perform a single pull."""
        if not player.spend_pull():
            return None

        pity.increment()
        rates = pity.get_effective_rates(self.base_rates)
        is_pity = pity.at_hard_pity or pity.at_epic_pity

        rarity = self._select_rarity(rates)
        character = self._select_character(rarity, banner)

        # Update pity counters
        if rarity == Rarity.LEGENDARY:
            pity.reset_legendary()
        elif rarity == Rarity.EPIC:
            pity.reset_epic()

        is_new = not player.has_character(character)
        is_featured = banner.is_featured(character) if banner else False
        player.add_character(character)

        return PullResult(
            character=character,
            is_new=is_new,
            is_featured=is_featured,
            is_pity=is_pity,
        )

    def multi_pull(
        self,
        player: Player,
        pity: PityCounter,
        banner: Banner | None = None,
    ) -> list[PullResult]:
        """Perform a 10-pull."""
        if not player.spend_multi_pull():
            return []

        results: list[PullResult] = []

        for i in range(player.MULTI_PULL_COUNT):
            pity.increment()
            rates = pity.get_effective_rates(self.base_rates)
            is_pity = pity.at_hard_pity or pity.at_epic_pity

            rarity = self._select_rarity(rates)

            # Guarantee at least one rare+ in a 10-pull
            if i == 9 and all(r.character.rarity == Rarity.COMMON for r in results):
                rarity = Rarity.RARE

            character = self._select_character(rarity, banner)

            if rarity == Rarity.LEGENDARY:
                pity.reset_legendary()
            elif rarity == Rarity.EPIC:
                pity.reset_epic()

            is_new = not player.has_character(character)
            is_featured = banner.is_featured(character) if banner else False
            player.add_character(character)

            results.append(
                PullResult(
                    character=character,
                    is_new=is_new,
                    is_featured=is_featured,
                    is_pity=is_pity,
                )
            )

        return results
