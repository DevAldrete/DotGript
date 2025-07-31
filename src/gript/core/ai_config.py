"""
Configuration management for AI features in DotGript.
Handles AI settings, API keys, and configuration updates.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt, Confirm


@dataclass
class AIConfig:
    """AI configuration settings."""
    default_personality: str = "geek"
    embedding_model: str = "text-embedding-3-small"
    embedding_provider: str = "openai"
    chat_model: str = "gpt-4o-mini"
    chat_provider: str = "openai"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_tokens_per_request: int = 4000
    index_file_types: list = None
    exclude_patterns: list = None
    auto_index_on_change: bool = True
    
    def __post_init__(self):
        if self.index_file_types is None:
            self.index_file_types = [".py", ".js", ".ts", ".md", ".txt", ".json", ".yaml", ".yml", ".toml"]
        if self.exclude_patterns is None:
            self.exclude_patterns = ["__pycache__", "node_modules", ".git", "*.pyc", "*.log"]


@dataclass
class UsageTrackingConfig:
    """Usage tracking configuration."""
    enabled: bool = True
    track_tokens: bool = True
    track_costs: bool = True
    monthly_budget_usd: float = 50.0


class AIConfigManager:
    """Manages AI configuration for DotGript projects."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.gript_dir = project_root / ".gript"
        self.config_file = self.gript_dir / ".conf.json"
        self.console = Console()
        
        # Ensure .gript directory exists
        self.gript_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """Load the current configuration."""
        if not self.config_file.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self._create_default_config()
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        ai_config = AIConfig()
        usage_config = UsageTrackingConfig()
        
        default_config = {
            "workflow_type": "github_flow",
            "branch_strategy": {
                "main_branch": "main",
                "develop_branch": "develop",
                "feature_prefix": "feature/",
                "hotfix_prefix": "hotfix/",
                "release_prefix": "release/",
                "bugfix_prefix": "bugfix/"
            },
            "enforce_conventional_commits": True,
            "auto_squash_merge": True,
            "semantic_versioning": True,
            "auto_changelog": True,
            "protected_branches": ["main", "master", "develop"],
            "max_commit_message_length": 72,
            "ai_config": asdict(ai_config),
            "ai_usage_stats": {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "monthly_requests": 0,
                "monthly_tokens": 0,
                "monthly_cost_usd": 0.0,
                "last_reset_date": None,
                "last_index_update": None
            }
        }
        
        default_config["ai_config"]["usage_tracking"] = asdict(usage_config)
        return default_config
    
    def setup_ai_config(self):
        """Interactive setup for AI configuration."""
        self.console.print("🤖 [bold cyan]AI Configuration Setup[/bold cyan]")
        self.console.print("Let's configure your AI settings for codebase analysis!")
        
        config = self.load_config()
        ai_config = config.setdefault("ai_config", {})
        
        # Check API keys
        self._setup_api_keys()
        
        # AI provider selection
        self.console.print("\n📡 [bold]AI Provider Settings[/bold]")
        
        chat_providers = ["openai", "openrouter"]
        current_chat_provider = ai_config.get("chat_provider", "openai")
        
        chat_provider = Prompt.ask(
            "Choose chat AI provider",
            choices=chat_providers,
            default=current_chat_provider
        )
        ai_config["chat_provider"] = chat_provider
        
        # Model selection based on provider
        if chat_provider == "openai":
            models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
            default_model = "gpt-4o-mini"
        else:
            models = ["anthropic/claude-3.5-sonnet", "meta-llama/llama-3.1-8b-instruct:free", "microsoft/wizardlm-2-8x22b"]
            default_model = "meta-llama/llama-3.1-8b-instruct:free"
        
        current_model = ai_config.get("chat_model", default_model)
        chat_model = Prompt.ask(
            "Choose chat model",
            choices=models,
            default=current_model
        )
        ai_config["chat_model"] = chat_model
        
        # Embedding provider
        embedding_providers = ["openai", "sentence-transformers"]
        current_embedding_provider = ai_config.get("embedding_provider", "openai")
        
        embedding_provider = Prompt.ask(
            "Choose embedding provider",
            choices=embedding_providers,
            default=current_embedding_provider
        )
        ai_config["embedding_provider"] = embedding_provider
        
        if embedding_provider == "openai":
            embedding_models = ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
            default_embedding = "text-embedding-3-small"
        else:
            embedding_models = ["all-MiniLM-L6-v2", "all-mpnet-base-v2"]
            default_embedding = "all-MiniLM-L6-v2"
        
        current_embedding = ai_config.get("embedding_model", default_embedding)
        embedding_model = Prompt.ask(
            "Choose embedding model",
            choices=embedding_models,
            default=current_embedding
        )
        ai_config["embedding_model"] = embedding_model
        
        # Personality
        personalities = ["geek", "wizard", "mom", "hater", "sexy", "nasty", "bro", "corporate"]
        current_personality = ai_config.get("default_personality", "geek")
        
        personality = Prompt.ask(
            "Choose default AI personality",
            choices=personalities,
            default=current_personality
        )
        ai_config["default_personality"] = personality
        
        # Indexing settings
        self.console.print("\n📚 [bold]Codebase Indexing Settings[/bold]")
        
        chunk_size = int(Prompt.ask(
            "Code chunk size (characters)",
            default=str(ai_config.get("chunk_size", 1000))
        ))
        ai_config["chunk_size"] = chunk_size
        
        auto_index = Confirm.ask(
            "Enable automatic re-indexing on file changes?",
            default=ai_config.get("auto_index_on_change", True)
        )
        ai_config["auto_index_on_change"] = auto_index
        
        # Budget settings
        self.console.print("\n💰 [bold]Usage Tracking & Budget[/bold]")
        
        track_usage = Confirm.ask(
            "Enable usage tracking?",
            default=ai_config.get("usage_tracking", {}).get("enabled", True)
        )
        
        if track_usage:
            monthly_budget = float(Prompt.ask(
                "Monthly budget (USD)",
                default=str(ai_config.get("usage_tracking", {}).get("monthly_budget_usd", 50.0))
            ))
            
            ai_config["usage_tracking"] = {
                "enabled": True,
                "track_tokens": True,
                "track_costs": True,
                "monthly_budget_usd": monthly_budget
            }
        else:
            ai_config["usage_tracking"] = {"enabled": False}
        
        # Save configuration
        self.save_config(config)
        
        self.console.print("\n✅ [green]AI configuration saved successfully![/green]")
        self._display_config_summary(ai_config)
    
    def _setup_api_keys(self):
        """Setup API keys for AI providers."""
        self.console.print("\n🔑 [bold]API Key Configuration[/bold]")
        
        # Check for existing keys
        openai_key = os.getenv("OPENAI_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        key_table = Table(title="Current API Keys")
        key_table.add_column("Provider", style="cyan")
        key_table.add_column("Status", style="green")
        
        key_table.add_row("OpenAI", "✅ Set" if openai_key else "❌ Not set")
        key_table.add_row("OpenRouter", "✅ Set" if openrouter_key else "❌ Not set")
        
        self.console.print(key_table)
        
        if not openai_key and not openrouter_key:
            self.console.print("\n[yellow]⚠️  No API keys found![/yellow]")
            self.console.print("Please set at least one API key in your environment:")
            self.console.print("• [cyan]export OPENAI_API_KEY='your-key'[/cyan]")
            self.console.print("• [cyan]export OPENROUTER_API_KEY='your-key'[/cyan]")
            self.console.print("\nOr add them to a .env file in your project root.")
    
    def _display_config_summary(self, ai_config: Dict[str, Any]):
        """Display a summary of the AI configuration."""
        summary_table = Table(title="AI Configuration Summary")
        summary_table.add_column("Setting", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Chat Provider", ai_config.get("chat_provider", "N/A"))
        summary_table.add_row("Chat Model", ai_config.get("chat_model", "N/A"))
        summary_table.add_row("Embedding Provider", ai_config.get("embedding_provider", "N/A"))
        summary_table.add_row("Embedding Model", ai_config.get("embedding_model", "N/A"))
        summary_table.add_row("Default Personality", ai_config.get("default_personality", "N/A"))
        summary_table.add_row("Chunk Size", str(ai_config.get("chunk_size", "N/A")))
        summary_table.add_row("Auto Index", "✅" if ai_config.get("auto_index_on_change") else "❌")
        
        usage_tracking = ai_config.get("usage_tracking", {})
        if usage_tracking.get("enabled"):
            budget = usage_tracking.get("monthly_budget_usd", 0)
            summary_table.add_row("Monthly Budget", f"${budget}")
        
        self.console.print(summary_table)
    
    def show_current_config(self):
        """Display the current AI configuration."""
        config = self.load_config()
        ai_config = config.get("ai_config", {})
        
        if not ai_config:
            self.console.print("[yellow]No AI configuration found. Run 'gript ai setup' to configure.[/yellow]")
            return
        
        self._display_config_summary(ai_config)
    
    def update_budget(self, new_budget: float):
        """Update the monthly budget."""
        config = self.load_config()
        ai_config = config.setdefault("ai_config", {})
        usage_tracking = ai_config.setdefault("usage_tracking", {})
        
        usage_tracking["monthly_budget_usd"] = new_budget
        usage_tracking["enabled"] = True
        
        self.save_config(config)
        self.console.print(f"✅ Monthly budget updated to ${new_budget}")
    
    def reset_usage_stats(self):
        """Reset usage statistics."""
        config = self.load_config()
        usage_stats = config.setdefault("ai_usage_stats", {})
        
        usage_stats.update({
            "monthly_requests": 0,
            "monthly_tokens": 0,
            "monthly_cost_usd": 0.0,
            "last_reset_date": None
        })
        
        self.save_config(config)
        self.console.print("✅ Usage statistics reset successfully!")
