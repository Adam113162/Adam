"""Tests for gacha.banner module."""

from datetime import datetime, timedelta

from gacha.banner import Banner, BannerManager
from gacha.models import Rarity


class TestBanner:
    def test_creation(self, banner):
        assert banner.name == "Test Banner"
        assert banner.featured_count == 2

    def test_is_active_no_dates(self):
        b = Banner(name="Always Active")
        assert b.is_active

    def test_is_active_within_dates(self):
        now = datetime.now()
        b = Banner(
            name="Current",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
        )
        assert b.is_active

    def test_not_active_before_start(self):
        b = Banner(
            name="Future",
            start_date=datetime.now() + timedelta(days=1),
        )
        assert not b.is_active

    def test_not_active_after_end(self):
        b = Banner(
            name="Expired",
            end_date=datetime.now() - timedelta(days=1),
        )
        assert not b.is_active

    def test_is_featured(self, banner, sample_characters):
        zeus = sample_characters[9]
        slime = sample_characters[0]
        assert banner.is_featured(zeus)
        assert not banner.is_featured(slime)

    def test_get_featured_by_rarity(self, banner):
        legends = banner.get_featured_by_rarity(Rarity.LEGENDARY)
        assert len(legends) == 1
        assert legends[0].name == "Zeus"

    def test_add_featured(self, banner, sample_characters):
        knight = sample_characters[3]
        banner.add_featured(knight)
        assert banner.featured_count == 3
        assert banner.is_featured(knight)

    def test_add_featured_no_duplicate(self, banner, sample_characters):
        zeus = sample_characters[9]
        banner.add_featured(zeus)
        assert banner.featured_count == 2  # already featured

    def test_remove_featured(self, banner, sample_characters):
        zeus = sample_characters[9]
        assert banner.remove_featured(zeus)
        assert not banner.is_featured(zeus)
        assert banner.featured_count == 1

    def test_remove_featured_not_found(self, banner, sample_characters):
        slime = sample_characters[0]
        assert not banner.remove_featured(slime)

    def test_rate_up_multiplier_default(self, banner):
        assert banner.rate_up_multiplier == 2.0


class TestBannerManager:
    def test_empty_manager(self):
        mgr = BannerManager()
        assert mgr.get_active_banners() == []

    def test_add_banner(self, banner):
        mgr = BannerManager()
        mgr.add_banner(banner)
        assert len(mgr.banners) == 1

    def test_get_active_banners(self, banner):
        mgr = BannerManager()
        expired = Banner(name="Expired", end_date=datetime.now() - timedelta(days=1))
        mgr.add_banner(banner)
        mgr.add_banner(expired)
        active = mgr.get_active_banners()
        assert len(active) == 1
        assert active[0].name == "Test Banner"

    def test_get_banner_by_name(self, banner):
        mgr = BannerManager()
        mgr.add_banner(banner)
        found = mgr.get_banner_by_name("Test Banner")
        assert found is banner

    def test_get_banner_by_name_not_found(self):
        mgr = BannerManager()
        assert mgr.get_banner_by_name("Nope") is None

    def test_remove_banner(self, banner):
        mgr = BannerManager()
        mgr.add_banner(banner)
        assert mgr.remove_banner("Test Banner")
        assert len(mgr.banners) == 0

    def test_remove_banner_not_found(self):
        mgr = BannerManager()
        assert not mgr.remove_banner("Nope")
