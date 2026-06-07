"""FastAPI web server for the gacha game."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from gacha.banner import Banner
from gacha.engine import GachaEngine, PullResult
from gacha.models import Character, CharacterPool, Rarity
from gacha.pity import PityCounter
from gacha.player import Player

app = FastAPI(title="Gacha Game")

# --- Game Data Setup ---
ALL_CHARACTERS = [
    # Common (Water, Earth, Wind, Fire)
    Character("Slime", Rarity.COMMON, "Water", 10, 5, 50),
    Character("Goblin", Rarity.COMMON, "Earth", 12, 4, 45),
    Character("Wolf", Rarity.COMMON, "Wind", 14, 3, 40),
    Character("Bat", Rarity.COMMON, "Fire", 11, 6, 48),
    Character("Rat", Rarity.COMMON, "Earth", 9, 7, 55),
    Character("Snake", Rarity.COMMON, "Wind", 13, 4, 42),
    # Rare
    Character("Knight", Rarity.RARE, "Fire", 25, 15, 80),
    Character("Mage", Rarity.RARE, "Water", 30, 10, 60),
    Character("Archer", Rarity.RARE, "Wind", 28, 12, 70),
    Character("Cleric", Rarity.RARE, "Earth", 20, 18, 90),
    Character("Ninja", Rarity.RARE, "Wind", 32, 8, 55),
    # Epic
    Character("Dragon", Rarity.EPIC, "Fire", 50, 30, 150),
    Character("Phoenix", Rarity.EPIC, "Fire", 55, 25, 140),
    Character("Kraken", Rarity.EPIC, "Water", 45, 35, 160),
    Character("Titan", Rarity.EPIC, "Earth", 40, 40, 180),
    # Legendary
    Character("Zeus", Rarity.LEGENDARY, "Lightning", 100, 50, 300),
    Character("Odin", Rarity.LEGENDARY, "Wind", 95, 55, 310),
    Character("Athena", Rarity.LEGENDARY, "Water", 90, 60, 320),
]

pool = CharacterPool(characters=ALL_CHARACTERS)
engine = GachaEngine(pool=pool)

# Session state (in-memory, per server instance)
player = Player(name="Player", currency=10000)
pity = PityCounter()
banner = Banner(
    name="Legendary Rate-Up: Zeus",
    featured_characters=[
        ALL_CHARACTERS[15],  # Zeus
        ALL_CHARACTERS[11],  # Dragon
    ],
)


# --- API Models ---
class CharacterResponse(BaseModel):
    name: str
    rarity: str
    element: str
    attack: int
    defense: int
    hp: int
    power_rating: int
    is_new: bool
    is_featured: bool
    is_pity: bool


class PullResponse(BaseModel):
    success: bool
    results: list[CharacterResponse]
    currency_remaining: int
    pity_count: int
    message: str


class PlayerState(BaseModel):
    name: str
    currency: int
    premium_currency: int
    inventory_size: int
    total_pulls: int
    pity_count: int
    soft_pity: bool
    unique_characters: int


# --- Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text())


@app.get("/api/state")
async def get_state() -> PlayerState:
    return PlayerState(
        name=player.name,
        currency=player.currency,
        premium_currency=player.premium_currency,
        inventory_size=player.inventory_size,
        total_pulls=player.total_pulls,
        pity_count=pity.pull_count,
        soft_pity=pity.in_soft_pity,
        unique_characters=len(player.get_unique_characters()),
    )


@app.post("/api/pull")
async def do_pull() -> PullResponse:
    result = engine.pull(player, pity, banner=banner)
    if result is None:
        return PullResponse(
            success=False,
            results=[],
            currency_remaining=player.currency,
            pity_count=pity.pull_count,
            message="Not enough currency! Need 160.",
        )
    return PullResponse(
        success=True,
        results=[_to_response(result)],
        currency_remaining=player.currency,
        pity_count=pity.pull_count,
        message=_pull_message(result),
    )


@app.post("/api/pull10")
async def do_multi_pull() -> PullResponse:
    results = engine.multi_pull(player, pity, banner=banner)
    if not results:
        return PullResponse(
            success=False,
            results=[],
            currency_remaining=player.currency,
            pity_count=pity.pull_count,
            message="Not enough currency! Need 1440 for a 10-pull.",
        )
    return PullResponse(
        success=True,
        results=[_to_response(r) for r in results],
        currency_remaining=player.currency,
        pity_count=pity.pull_count,
        message=f"Got {len(results)} characters!",
    )


@app.post("/api/add-currency")
async def add_currency() -> PlayerState:
    player.add_currency(1600)
    return await get_state()


@app.get("/api/inventory")
async def get_inventory() -> list[CharacterResponse]:
    chars = player.inventory
    seen: set[str] = set()
    unique_inventory: list[CharacterResponse] = []
    for char in chars:
        key = char.name
        if key not in seen:
            seen.add(key)
            unique_inventory.append(
                CharacterResponse(
                    name=char.name,
                    rarity=char.rarity.value,
                    element=char.element,
                    attack=char.attack,
                    defense=char.defense,
                    hp=char.hp,
                    power_rating=char.power_rating,
                    is_new=False,
                    is_featured=banner.is_featured(char),
                    is_pity=False,
                )
            )
    unique_inventory.sort(
        key=lambda c: ["legendary", "epic", "rare", "common"].index(c.rarity)
    )
    return unique_inventory


@app.get("/api/banner")
async def get_banner():
    return {
        "name": banner.name,
        "featured": [
            {"name": c.name, "rarity": c.rarity.value, "element": c.element}
            for c in banner.featured_characters
        ],
    }


def _to_response(result: PullResult) -> CharacterResponse:
    return CharacterResponse(
        name=result.character.name,
        rarity=result.character.rarity.value,
        element=result.character.element,
        attack=result.character.attack,
        defense=result.character.defense,
        hp=result.character.hp,
        power_rating=result.character.power_rating,
        is_new=result.is_new,
        is_featured=result.is_featured,
        is_pity=result.is_pity,
    )


def _pull_message(result: PullResult) -> str:
    parts = []
    if result.is_pity:
        parts.append("PITY!")
    if result.is_new:
        parts.append("NEW!")
    if result.is_featured:
        parts.append("FEATURED!")
    rarity_label = result.character.rarity.value.upper()
    return f"[{rarity_label}] {result.character.name} " + " ".join(parts)
