from dataclasses import dataclass
import enum
import asyncio
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent, RunContext
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from gript.core.settings import settings
from gript.core.ai_codebase import CodebaseIndexer, CodebaseAnalysisAgent
from typer import Typer
from rich import print
from rich.table import Table
from rich.console import Console

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
@app.command("ask")
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


@app.command("setup")
def setup_ai_config(project_root: str = "."):
    """Interactive setup for AI configuration."""
    from gript.core.ai_config import AIConfigManager
    
    project_path = Path(project_root).resolve()
    config_manager = AIConfigManager(project_path)
    
    config_manager.setup_ai_config()


@app.command("config-show")
def show_ai_config(project_root: str = "."):
    """Show current AI configuration."""
    from gript.core.ai_config import AIConfigManager
    
    project_path = Path(project_root).resolve()
    config_manager = AIConfigManager(project_path)
    
    config_manager.show_current_config()


@app.command("budget")
def update_budget(
    amount: float,
    project_root: str = ".",
):
    """Update monthly AI usage budget."""
    from gript.core.ai_config import AIConfigManager
    
    project_path = Path(project_root).resolve()
    config_manager = AIConfigManager(project_path)
    
    config_manager.update_budget(amount)


@app.command("reset-stats")
def reset_usage_stats(project_root: str = "."):
    """Reset AI usage statistics."""
    from gript.core.ai_config import AIConfigManager
    
    project_path = Path(project_root).resolve()
    config_manager = AIConfigManager(project_path)
    
    config_manager.reset_usage_stats()


@app.command("help")
def show_ai_help():
    """Show help information about AI features."""
    from gript.core.ai_init import display_ai_features_help
    
    display_ai_features_help()


# CODEBASE ANALYSIS COMMANDS
@app.command("analyze")
def analyze_codebase(
    query: str,
    persona: Personality = Personality.GEEK,
    index_first: bool = False,
    project_root: str = ".",
):
    """Analyze the codebase and answer questions about it using AI."""
    console = Console()
    project_path = Path(project_root).resolve()
    config_path = project_path / ".gript" / ".conf.json"
    
    if not config_path.exists():
        print("[red]❌ No .gript configuration found. Please run 'gript git init' first.[/red]")
        return
    
    try:
        # Initialize indexer and analysis agent
        indexer = CodebaseIndexer(project_path, config_path)
        analysis_agent = CodebaseAnalysisAgent(indexer)
        
        # Index codebase if requested or if no index exists
        if index_first or not indexer.collection.count():
            console.print("🔍 Indexing codebase...")
            indexer.index_codebase()
        
        # Get personality info
        persona_name = persona.value.lower()
        
        console.print(f"🤖 Analyzing codebase with {persona_name} personality...")
        
        # Run analysis
        async def run_analysis():
            return await analysis_agent.analyze_codebase(query, persona_name)
        
        response = asyncio.run(run_analysis())
        
        # Display usage stats
        stats = indexer.get_usage_stats()
        usage_table = Table(title="AI Usage Stats")
        usage_table.add_column("Metric", style="cyan")
        usage_table.add_column("Value", style="green")
        
        usage_table.add_row("Monthly Requests", str(stats.monthly_requests))
        usage_table.add_row("Monthly Tokens", str(stats.monthly_tokens))
        usage_table.add_row("Monthly Cost", f"${stats.monthly_cost_usd:.4f}")
        usage_table.add_row("Total Requests", str(stats.total_requests))
        
        console.print("\n")
        console.print(usage_table)
        console.print("\n")
        print(response)
        
        # Cleanup
        indexer.cleanup()
        
    except Exception as e:
        print(f"[red]❌ Error analyzing codebase: {e}[/red]")


@app.command("index")
def index_codebase(
    project_root: str = ".",
    force: bool = False,
):
    """Index the codebase for AI analysis."""
    console = Console()
    project_path = Path(project_root).resolve()
    config_path = project_path / ".gript" / ".conf.json"
    
    if not config_path.exists():
        print("[red]❌ No .gript configuration found. Please run 'gript git init' first.[/red]")
        return
    
    try:
        indexer = CodebaseIndexer(project_path, config_path)
        indexer.index_codebase(force_reindex=force)
        
        # Show stats
        collection_count = indexer.collection.count()
        console.print(f"📊 Vector database contains {collection_count} code chunks")
        
        indexer.cleanup()
        
    except Exception as e:
        print(f"[red]❌ Error indexing codebase: {e}[/red]")


@app.command("search-code")
def search_similar_code(
    query: str,
    project_root: str = ".",
    max_results: int = 5,
):
    """Search for code similar to the query using embeddings."""
    console = Console()
    project_path = Path(project_root).resolve()
    config_path = project_path / ".gript" / ".conf.json"
    
    if not config_path.exists():
        print("[red]❌ No .gript configuration found. Please run 'gript git init' first.[/red]")
        return
    
    try:
        indexer = CodebaseIndexer(project_path, config_path)
        results = indexer.search_similar_code(query, n_results=max_results)
        
        if not results:
            print("[yellow]No similar code found. Try indexing first with 'gript ai index'[/yellow]")
            return
        
        results_table = Table(title=f"Similar Code for: '{query}'")
        results_table.add_column("File", style="cyan")
        results_table.add_column("Lines", style="yellow")
        results_table.add_column("Similarity", style="green")
        results_table.add_column("Language", style="magenta")
        
        for result in results:
            metadata = result["metadata"]
            similarity = f"{result['similarity']:.2f}"
            lines = f"{metadata['start_line']}-{metadata['end_line']}"
            
            results_table.add_row(
                metadata["file_path"],
                lines,
                similarity,
                metadata["language"]
            )
        
        console.print(results_table)
        
        # Show first result's content
        if results:
            console.print("\n[bold]Most similar code:[/bold]")
            console.print(f"[cyan]{results[0]['metadata']['file_path']}[/cyan]")
            console.print("```")
            console.print(results[0]["content"][:500] + ("..." if len(results[0]["content"]) > 500 else ""))
            console.print("```")
        
        indexer.cleanup()
        
    except Exception as e:
        print(f"[red]❌ Error searching code: {e}[/red]")


@app.command("usage")
def show_usage_stats(project_root: str = "."):
    """Show AI usage statistics."""
    console = Console()
    project_path = Path(project_root).resolve()
    config_path = project_path / ".gript" / ".conf.json"
    
    if not config_path.exists():
        print("[red]❌ No .gript configuration found. Please run 'gript git init' first.[/red]")
        return
    
    try:
        indexer = CodebaseIndexer(project_path, config_path)
        stats = indexer.get_usage_stats()
        
        # Monthly stats table
        monthly_table = Table(title="Monthly AI Usage")
        monthly_table.add_column("Metric", style="cyan")
        monthly_table.add_column("Value", style="green")
        
        monthly_table.add_row("Requests", str(stats.monthly_requests))
        monthly_table.add_row("Tokens", str(stats.monthly_tokens))
        monthly_table.add_row("Cost (USD)", f"${stats.monthly_cost_usd:.4f}")
        monthly_table.add_row("Last Reset", stats.last_reset_date or "Never")
        
        # Total stats table
        total_table = Table(title="Total AI Usage")
        total_table.add_column("Metric", style="cyan")
        total_table.add_column("Value", style="green")
        
        total_table.add_row("Total Requests", str(stats.total_requests))
        total_table.add_row("Total Tokens", str(stats.total_tokens))
        total_table.add_row("Total Cost (USD)", f"${stats.total_cost_usd:.4f}")
        total_table.add_row("Last Index Update", stats.last_index_update or "Never")
        
        console.print(monthly_table)
        console.print(total_table)
        
        # Budget warning
        ai_config = indexer.config.get("ai_config", {})
        budget = ai_config.get("usage_tracking", {}).get("monthly_budget_usd", 50.0)
        
        if stats.monthly_cost_usd > budget * 0.8:
            console.print(f"[yellow]⚠️  Warning: You've used {stats.monthly_cost_usd/budget:.1%} of your monthly budget (${budget})[/yellow]")
        
    except Exception as e:
        print(f"[red]❌ Error getting usage stats: {e}[/red]")
