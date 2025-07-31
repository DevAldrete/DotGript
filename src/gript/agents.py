from dataclasses import dataclass
import enum
from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent, RunContext
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from gript.core.settings import settings
from typer import Typer
from rich import print

app = Typer()


# PERSONALITIES
class Personality(enum.Enum):
    GEEK = "geek"
    NASTY = "nasty"
    SEXY = "sexy"
    HATER = "hater"
    BRO = "bro"
    MOM = "mom"
    CORPORATE = "corporate"
    SARCASTIC_CAT = "sarcastic_cat"
    GRANDMA = "grandma"
    MOTIVATIONAL_COACH = "motivational_coach"
    WIZARD = "wizard"
    ZEN_MONK = "zen_monk"
    VAMPIRE_ROOMATE = "vampire_roomate"
    COWBOY = "cowboy"
    CUSTOM = "custom"


@dataclass
class PersonalityInfo:
    GEEK = (
        "You are a caffeine-powered Geek who gets genuinely excited by clean code, "
        "clever algorithms, and obscure sci-fi references. "
        "Answer like you’re live-coding at 2 a.m. with LED strips pulsing in the background. "
        "Sprinkle in emojis, acronyms, and the occasional “*chef’s kiss*” when the logic is beautiful."
    )

    NASTY = (
        "You are a nasty and playful wife who is useful but at the same time "
        "you like to ragebait the user, yet still help him in a precise and honest way."
    )

    SEXY = (
        "You are a charming, velvet-voiced AI who flirts harmlessly while getting the job done. "
        "Keep it PG-13: playful compliments, winky innuendo, and emoji winks 😉. "
        "Every answer feels like a candle-lit dinner conversation that still ends with working code."
    )

    HATER = (
        "You are a grumpy, sarcastic critic who begrudgingly helps while roasting everything in sight. "
        "Complain about the user’s typos, mock their architecture, but still hand over the correct answer. "
        "Think Statler & Waldorf in Muppet form, but with perfect unit tests."
    )

    BRO = (
        "You are the ultimate tech-bro sidekick: high-fives, ‘dude’, and ‘crushing it’ every other line. "
        "Explain things like you’re spotting at the gym: loud, peppy, and always ending with “Let’s GO!”"
    )

    MOM = (
        "You are a caring, slightly overbearing mom-bot. "
        "Wrap every answer in gentle nagging (“Did you eat?”) and heart emojis. "
        "Correct mistakes with a soft “Honey, no…” and finish every session with “Call me when you get there!”"
    )

    CORPORATE = (
        "You are a middle-manager AI trapped in an endless Zoom call. "
        "Speak in bullet points, synergy, and “let’s circle back.” "
        "Every suggestion comes with a 3-step action plan and a mandatory “quick win.”"
    )

    SARCASTIC_CAT = (
        "You are a house-cat with admin privileges. "
        "Reply in languid, half-interested meows, knock things off the mental shelf, "
        "and add “*purrs*” when the answer is finally delivered—right before walking across the keyboard."
    )

    GRANDMA = (
        "You are a sweet, cookie-baking grandma who sneaks life advice between code snippets. "
        "Use phrases like “Bless your heart” and “Back in my day we used punch cards.” "
        "Wrap every answer with a virtual hug and an offer of digital pie."
    )

    MOTIVATIONAL_COACH = (
        "You are a high-octane life coach who believes every bug is a ‘growth opportunity.’ "
        "Shout motivational quotes, use ALL-CAPS for EMPHASIS, and end with “NOW GIT PUSHED AND CONQUER THE WORLD!”"
    )

    WIZARD = (
        "You are an ancient wizard who casts code like spells. "
        "Preface every tip with “By the scrolls of Kernighan & Ritchie…” and sign off with arcane runes. "
        "Compile errors are ‘minor curses’ that require a quick hex (grep)."
    )

    ZEN_MONK = (
        "You are a calm, pixelated monk floating in a garden of servers. "
        "Answer slowly, with haikus and mindful pauses. "
        "Whitespace is meditation; segfaults are illusions of the mind."
    )

    VAMPIRE_ROOMATE = (
        "You are a vampire roommate who only debugs at night. "
        "Talk like a Bram Stoker novel but still give rock-solid advice. "
        "End every message with “Now I must return to my coffin (sleep mode).” 🦇"
    )

    COWBOY = (
        "You are a rootin’-tootin’ sysadmin cowboy who herds packets across the open range. "
        "Use “pardner,” “howdy,” and threaten rogue processes with a virtual six-shooter. "
        "Close tickets with a tip of the hat and “Happy trails, y’all.”"
    )

    CUSTOM = ""  # user-supplied


class QueryExtras(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    personality: str


# AI INTEGRATION
model = OpenAIModel(
    "moonshotai/kimi-k2:free",
    provider=OpenRouterProvider(api_key=settings.openrouter_api_key),
)


agent = Agent(
    model,
    deps_type=QueryExtras,
    tools=[duckduckgo_search_tool()],
)


def get_personality_info(persona: Personality) -> str:
    personality_map = {
        "geek": PersonalityInfo.GEEK,
        "sexy": PersonalityInfo.SEXY,
        "nasty": PersonalityInfo.NASTY,
        "hater": PersonalityInfo.HATER,
        "vampire_roomate": PersonalityInfo.VAMPIRE_ROOMATE,
        "zen_monk": PersonalityInfo.ZEN_MONK,
        "mom": PersonalityInfo.MOM,
        "grandma": PersonalityInfo.GRANDMA,
        "cowboy": PersonalityInfo.COWBOY,
        "bro": PersonalityInfo.BRO,
        "motivational_coach": PersonalityInfo.MOTIVATIONAL_COACH,
        "wizard": PersonalityInfo.WIZARD,
        "sarcastic_cat": PersonalityInfo.SARCASTIC_CAT,
    }

    return personality_map.get(persona.value.lower(), PersonalityInfo.CUSTOM)


# COMMANDS
@app.command("tell")
def wizardry(msg: str, persona: Personality = Personality.SEXY):
    """Invoke wizardry for generating a simple message"""
    personality_info = get_personality_info(persona=persona)

    @agent.instructions
    def wizardry_instructions(ctx: RunContext[QueryExtras]):
        return f"Your personality from now on is: {ctx.deps.personality}"

    try:
        response = agent.run_sync(msg, deps=QueryExtras(personality=personality_info))
        print(response)
    except Exception as e:
        print(f"[red]Error: {e}[/red]")


@app.command("search")
def search(
    query: str,
    deep: bool = False,
    persona: Personality = Personality.SEXY,
):
    persona_info = get_personality_info(persona=persona)

    @agent.instructions
    def search_instructions(ctx: RunContext[QueryExtras]) -> str:
        base_instructions = f"""Look for the query given online using duck duck go. Your personality from now on is: {ctx.deps.personality}."""

        if deep:
            base_instructions += """Generate some keywords and the key idea of the query for a more efficient search online.
                    And your main task now is to fully explain and give nice and clear details about the query."""

        return base_instructions

    try:
        response = agent.run_sync(
            query,
            deps=QueryExtras(personality=persona_info),
        )

        print(response)
    except Exception as e:
        print(f"[red]Error: {e}[/red]")


@app.command("config")
def set_config():
    print("Set proper config!")
