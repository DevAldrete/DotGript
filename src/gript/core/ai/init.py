"""
AI system initialization utilities for DotGript.
Handles setup and initialization of AI features when creating new projects.
"""
from pathlib import Path
from gript.core.ai.config import AIConfigManager
from rich.console import Console


def initialize_ai_system(project_root: Path, interactive: bool = False) -> bool:
    """
    Initialize the AI system for a DotGript project.
    
    Args:
        project_root: Path to the project root
        interactive: Whether to run interactive setup
        
    Returns:
        bool: True if initialization was successful
    """
    console = Console()
    
    try:
        config_manager = AIConfigManager(project_root)
        
        # Create default configuration
        config = config_manager.load_config()
        
        if interactive:
            console.print("🤖 Setting up AI features...")
            config_manager.setup_ai_config()
        else:
            # Just ensure the config exists with defaults
            config_manager.save_config(config)
            console.print("✅ AI system initialized with default settings")
            console.print("💡 Run 'gript ai setup' for interactive configuration")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize AI system: {e}[/red]")
        return False


def check_ai_prerequisites() -> tuple[bool, list[str]]:
    """
    Check if prerequisites for AI features are met.
    
    Returns:
        tuple: (prerequisites_met, list_of_missing_items)
    """
    import os
    import importlib.util
    
    missing = []
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("OPENROUTER_API_KEY"):
        missing.append("API keys (OPENAI_API_KEY or OPENROUTER_API_KEY)")
    
    # Check for required packages
    required_packages = ["chromadb", "sentence_transformers", "tiktoken", "watchdog"]
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing.append(f"Required package: {package}")
    
    return len(missing) == 0, missing


def display_ai_features_help():
    """Display help information about AI features."""
    console = Console()
    
    console.print("🤖 [bold cyan]DotGript AI Features[/bold cyan]")
    console.print()
    
    console.print("[bold]Available Commands:[/bold]")
    console.print("• [cyan]gript ai setup[/cyan] - Interactive AI configuration")
    console.print("• [cyan]gript ai analyze <query>[/cyan] - Analyze codebase with AI")
    console.print("• [cyan]gript ai index[/cyan] - Index codebase for analysis")
    console.print("• [cyan]gript ai search-code <query>[/cyan] - Search similar code")
    console.print("• [cyan]gript ai usage[/cyan] - Show usage statistics")
    console.print("• [cyan]gript ai config-show[/cyan] - Show current configuration")
    console.print()
    
    console.print("[bold]Prerequisites:[/bold]")
    prerequisites_met, missing = check_ai_prerequisites()
    
    if prerequisites_met:
        console.print("✅ All prerequisites met!")
    else:
        console.print("[yellow]Missing prerequisites:[/yellow]")
        for item in missing:
            console.print(f"  ❌ {item}")
        console.print()
        console.print("[bold]Setup Instructions:[/bold]")
        console.print("1. Install dependencies: [cyan]uv sync[/cyan]")
        console.print("2. Set API key: [cyan]export OPENAI_API_KEY='your-key'[/cyan]")
        console.print("3. Run setup: [cyan]gript ai setup[/cyan]")
