"""Banner system for rate-up events."""

from dataclasses import dataclass, field
from datetime import datetime

from gacha.models import Character, Rarity


@dataclass
class Banner:
    """A gacha banner with featured/rate-up characters."""

    name: str
    featured_characters: list[Character] = field(default_factory=list)
    rate_up_multiplier: float = 2.0
    start_date: datetime | None = None
    end_date: datetime | None = None

    @property
    def is_active(self) -> bool:
        """Check if the banner is currently active."""
        now = datetime.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    def is_featured(self, character: Character) -> bool:
        """Check if a character is featured on this banner."""
        return character in self.featured_characters

    def get_featured_by_rarity(self, rarity: Rarity) -> list[Character]:
        """Get featured characters of a specific rarity."""
        return [c for c in self.featured_characters if c.rarity == rarity]

    @property
    def featured_count(self) -> int:
        """Number of featured characters."""
        return len(self.featured_characters)

    def add_featured(self, character: Character) -> None:
        """Add a character to the featured list."""
        if character not in self.featured_characters:
            self.featured_characters.append(character)

    def remove_featured(self, character: Character) -> bool:
        """Remove a character from the featured list."""
        if character in self.featured_characters:
            self.featured_characters.remove(character)
            return True
        return False


@dataclass
class BannerManager:
    """Manages multiple banners."""

    banners: list[Banner] = field(default_factory=list)

    def add_banner(self, banner: Banner) -> None:
        """Add a banner."""
        self.banners.append(banner)

    def get_active_banners(self) -> list[Banner]:
        """Get all currently active banners."""
        return [b for b in self.banners if b.is_active]

    def get_banner_by_name(self, name: str) -> Banner | None:
        """Find a banner by name."""
        for b in self.banners:
            if b.name == name:
                return b
        return None

    def remove_banner(self, name: str) -> bool:
        """Remove a banner by name."""
        banner = self.get_banner_by_name(name)
        if banner:
            self.banners.remove(banner)
            return True
        return False
