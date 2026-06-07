# Gacha Game Engine

A Python gacha game engine with pull mechanics, pity system, banners, and player management.

## Features

- **Character system** with rarities (Common, Rare, Epic, Legendary) and elemental types
- **Gacha engine** with weighted probability pulls
- **Pity system** with soft pity, hard pity, and epic guarantees
- **Banner system** with rate-up featured characters
- **Player management** with inventory, currency, and pull history
- **10-pull guarantee** — at least one Rare or better in every multi-pull

## Setup

```bash
python -m pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=src/gacha --cov-report=term-missing
```

## Linting

```bash
ruff check src/ tests/
```

## Project Structure

```
src/gacha/
├── __init__.py    # Package exports
├── models.py      # Character, Rarity, CharacterPool
├── engine.py      # GachaEngine (pull logic)
├── pity.py        # PityCounter (pity system)
├── banner.py      # Banner & BannerManager
└── player.py      # Player state
tests/
├── conftest.py    # Shared fixtures
├── test_models.py
├── test_engine.py
├── test_pity.py
├── test_banner.py
└── test_player.py
```
