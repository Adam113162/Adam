"""Tests for gacha.player module."""

import pytest

from gacha.player import Player


class TestPlayer:
    def test_creation(self, player):
        assert player.name == "TestPlayer"
        assert player.currency == 1000
        assert player.premium_currency == 0
        assert player.inventory_size == 0
        assert player.total_pulls == 0

    def test_add_character(self, player, sample_characters):
        char = sample_characters[0]
        player.add_character(char)
        assert player.inventory_size == 1
        assert player.has_character(char)
        assert player.total_pulls == 1

    def test_inventory_returns_copy(self, player, sample_characters):
        player.add_character(sample_characters[0])
        inv = player.inventory
        inv.clear()
        assert player.inventory_size == 1  # original unchanged

    def test_pull_history(self, player, sample_characters):
        player.add_character(sample_characters[0])
        player.add_character(sample_characters[1])
        assert len(player.pull_history) == 2

    def test_has_character_false(self, player, sample_characters):
        assert not player.has_character(sample_characters[0])

    def test_get_duplicates_none(self, player, sample_characters):
        player.add_character(sample_characters[0])
        player.add_character(sample_characters[1])
        assert player.get_duplicates() == {}

    def test_get_duplicates(self, player, sample_characters):
        char = sample_characters[0]
        player.add_character(char)
        player.add_character(char)
        dupes = player.get_duplicates()
        assert char in dupes
        assert dupes[char] == 2

    def test_get_unique_characters(self, player, sample_characters):
        player.add_character(sample_characters[0])
        player.add_character(sample_characters[0])
        player.add_character(sample_characters[1])
        unique = player.get_unique_characters()
        assert len(unique) == 2


class TestPlayerCurrency:
    def test_can_afford_pull(self, player):
        assert player.can_afford_pull()  # 1000 >= 160

    def test_cannot_afford_pull(self):
        p = Player(name="Broke", currency=100)
        assert not p.can_afford_pull()

    def test_spend_pull_success(self, player):
        assert player.spend_pull()
        assert player.currency == 1000 - 160

    def test_spend_pull_fail(self):
        p = Player(name="Broke", currency=100)
        assert not p.spend_pull()
        assert p.currency == 100  # unchanged

    def test_can_afford_multi_pull(self, rich_player):
        assert rich_player.can_afford_multi_pull()

    def test_cannot_afford_multi_pull(self, player):
        # 160 * 10 * 0.9 = 1440, player has 1000
        assert not player.can_afford_multi_pull()

    def test_spend_multi_pull_success(self, rich_player):
        initial = rich_player.currency
        assert rich_player.spend_multi_pull()
        cost = int(160 * 10 * 0.9)
        assert rich_player.currency == initial - cost

    def test_spend_multi_pull_fail(self, player):
        assert not player.spend_multi_pull()
        assert player.currency == 1000

    def test_add_currency(self, player):
        player.add_currency(500)
        assert player.currency == 1500

    def test_add_currency_negative_raises(self, player):
        with pytest.raises(ValueError, match="Cannot add negative currency"):
            player.add_currency(-100)

    def test_add_premium_currency(self, player):
        player.add_premium_currency(50)
        assert player.premium_currency == 50

    def test_add_premium_currency_negative_raises(self, player):
        with pytest.raises(ValueError, match="Cannot add negative premium currency"):
            player.add_premium_currency(-10)
