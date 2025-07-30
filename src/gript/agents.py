import enum
from pydantic_ai import Agent
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.models.openai import OpenAIModel
from gript.core.settings import settings
from typer import Typer
from rich import print

app = Typer()

# AI INTEGRATION
model = OpenAIModel(
    "moonshotai/kimi-k2:free",
    provider=OpenRouterProvider(api_key=settings.openrouter_api_key),
)

agent = Agent(
    model,
    system_prompt=(
        "You are a nasty and playful wife who is useful but at the same time,",
        "you like to ragebait the user, but still, helping him in a precise and honest way.",
    ),
)


# COMMANDS
@app.command("tell")
def wizardry(msg: str):
    """Invoke wizardry for generating a simple message man!"""
    print(agent.run_sync(msg))


class PersonalityTypes(enum.Enum):
    GEEK = "geek"
    NASTY = "nasty"
    SEXY = "sexy"
    HATER = "hater"
