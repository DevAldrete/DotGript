from typer import Typer
from gript.core.gript import (
    clone_repo, get_repo_info, push_changes, pull_changes, 
    get_repo_status, checkout_branch, switch_branch, remove_branch, add_remote, 
    get_current_branch, get_remote_repos, fetch_remote, list_branches,
    get_git_log, show_commit, get_diff, reset_repo, create_tag, list_tags, delete_tag,
    stash_changes, stash_pop, list_stashes, merge_branch, rebase_branch, cherry_pick,
    init_repo, get_untracked_files, add_files, remove_files, blame_file,
    GitError, GriptGit, create_gript_git, setup_gript_automation, get_gript_status, migrate_to_gript
)
from git import Repo
from typing import Optional, List
from rich import print
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

app = Typer()
console = Console()

@app.command("init")
def init_repository(
    path: str = ".",
    bare: bool = False,
    setup_gript: bool = True,
    workflow: str = "github_flow",
) -> None:
    """
    Initialize a new Git repository with DotGript automation.
    
    :param path: Path where to initialize the repository (default is current directory).
    :param bare: Whether to create a bare repository.
    :param setup_gript: Whether to automatically setup .gript folder and automation.
    :param workflow: Workflow type (github_flow, gitflow, gitlab_flow, custom).
    """
    try:
        repo = init_repo(path, bare, setup_gript)
        
        if bare:
            print(f"Initialized empty [yellow]bare[/yellow] Git repository in [green]{repo.git_dir}[/green]")
        else:
            print(f"Initialized empty Git repository in [green]{repo.git_dir}[/green]")
            
            if setup_gript:
                # Setup DotGript automation
                setup_gript_automation(path, workflow)
                print(f"✨ [bold green]DotGript automation configured[/bold green] with [cyan]{workflow}[/cyan] workflow")
                print("📁 Created [blue].gript/[/blue] folder with automation configs")
                print("🎯 Features enabled: operation logging, statistics tracking, branch metadata")
                
    except GitError as e:
        print(f"[red]Error:[/red] {e}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("log")
def get_log(
    local_path: str = ".",
    max_count: int = 10,
    oneline: bool = False,
    since: Optional[str] = None,
    until: Optional[str] = None,
    author: Optional[str] = None,
    grep: Optional[str] = None,
    graph: bool = False,
) -> None:
    """
    Show commit logs with enhanced filtering options.
    
    :param local_path: Local path of the repository.
    :param max_count: Maximum number of commits to show.
    :param oneline: Format as one line per commit.
    :param since: Show commits after this date (e.g., "2023-01-01", "1 week ago").
    :param until: Show commits before this date.
    :param author: Filter commits by author name or email.
    :param grep: Filter commits by message content.
    :param graph: Show a text-based graph of branches.
    """
    try:
        repo = Repo(local_path)
        logs = get_git_log(repo, max_count, oneline, since, until, author, grep, graph)
        
        if oneline:
            for log_entry in logs:
                short_hash = log_entry.get('short_hash', '')
                message = log_entry.get('message', '').split('\n')[0]
                print(f"[yellow]{short_hash}[/yellow] {message}")
        else:
            for log_entry in logs:
                # Create a formatted display for each commit
                table = Table(show_header=False, box=None, padding=(0, 1))
                table.add_column("Field", style="bold cyan")
                table.add_column("Value")
                
                table.add_row("Commit", f"[yellow]{log_entry.get('hash', '')}[/yellow]")
                table.add_row("Author", f"{log_entry.get('author_name', '')} <{log_entry.get('author_email', '')}>")
                table.add_row("Date", log_entry.get('author_date', ''))
                table.add_row("Message", log_entry.get('message', ''))
                
                console.print(table)
                print()
                
    except GitError as e:
        print(f"[red]Error:[/red] {e}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("show")
def show_commit_details(
    commit_ref: str = "HEAD",
    local_path: str = ".",
    show_stats: bool = True,
) -> None:
    """
    Show detailed information about a specific commit.
    
    :param commit_ref: Reference to the commit (hash, HEAD, etc.).
    :param local_path: Local path of the repository.
    :param show_stats: Whether to include file change statistics.
    """
    try:
        repo = Repo(local_path)
        commit_info = show_commit(repo, commit_ref, show_stats)
        
        # Display commit information in a formatted table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="bold cyan")
        table.add_column("Value")
        
        table.add_row("Commit", f"[yellow]{commit_info['hash']}[/yellow]")
        table.add_row("Author", f"{commit_info['author_name']} <{commit_info['author_email']}>")
        table.add_row("Date", commit_info['author_date'])
        table.add_row("Committer", f"{commit_info['committer_name']} <{commit_info['committer_email']}>")
        table.add_row("Commit Date", commit_info['commit_date'])
        
        if commit_info['parents']:
            table.add_row("Parents", ", ".join(commit_info['parents']))
        
        # Stats
        if show_stats:
            stats = f"{commit_info['files_changed']} files changed"
            if commit_info['insertions'] > 0:
                stats += f", {commit_info['insertions']} insertions(+)"
            if commit_info['deletions'] > 0:
                stats += f", {commit_info['deletions']} deletions(-)"
            table.add_row("Changes", stats)
        
        console.print(table)
        print()
        print("[bold]Message:[/bold]")
        print(commit_info['message'])
        
        # Show diff if available
        if commit_info.get('diff') and show_stats:
            print("\n[bold]Diff:[/bold]")
            syntax = Syntax(commit_info['diff'], "diff", theme="monokai", line_numbers=False)
            console.print(syntax)
            
    except GitError as e:
        print(f"[red]Error:[/red] {e}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("diff")
def show_diff(
    local_path: str = ".",
    cached: bool = False,
    commit1: Optional[str] = None,
    commit2: Optional[str] = None,
    file_path: Optional[str] = None,
    context_lines: int = 3,
    word_diff: bool = False,
) -> None:
    """
    Show changes between commits, commit and working tree, etc.
    
    :param local_path: Local path of the repository.
    :param cached: Show staged changes.
    :param commit1: First commit to compare (if None, uses HEAD).
    :param commit2: Second commit to compare (if None, uses working dir).
    :param file_path: Specific file to show diff for.
    :param context_lines: Number of context lines to show.
    :param word_diff: Show word-level differences.
    """
    try:
        repo = Repo(local_path)
        diff_data = get_diff(repo, cached, commit1, commit2, file_path, context_lines, word_diff)
        
        # Show statistics summary
        stats = diff_data['stats']
        if stats['files_changed'] > 0:
            summary = f"{stats['files_changed']} files changed"
            if stats['insertions'] > 0:
                summary += f", {stats['insertions']} insertions(+)"
            if stats['deletions'] > 0:
                summary += f", {stats['deletions']} deletions(-)"
            print(f"[bold cyan]{summary}[/bold cyan]")
            print()
        
        # Show the diff
        if diff_data['diff_text']:
            syntax = Syntax(diff_data['diff_text'], "diff", theme="monokai", line_numbers=False)
            console.print(syntax)
        else:
            print("No differences found.")
            
    except GitError as e:
        print(f"[red]Error:[/red] {e}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("reset")
def reset_repository(
    mode: str = "mixed",
    commit_ref: str = "HEAD",
    local_path: str = ".",
) -> None:
    """
    Reset current HEAD to the specified state.
    
    :param mode: Reset mode ('soft', 'mixed', 'hard').
    :param commit_ref: Reference to reset to.
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        reset_repo(repo, mode, commit_ref)
        print(f"Reset repository to [bold]{commit_ref}[/bold] with mode [bold]{mode}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("add")
def add_files_to_staging(
    files: List[str],
    local_path: str = ".",
) -> None:
    """
    Add files to the staging area.
    
    :param files: List of file paths to add.
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        if not files:
            # Add all files if none specified
            repo.git.add(A=True)
            print("Added [green]all changes[/green] to staging area")
        else:
            add_files(repo, files)
            print(f"Added [green]{', '.join(files)}[/green] to staging area")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("remove")
def remove_files_from_repo(
    files: List[str],
    local_path: str = ".",
    cached: bool = False,
) -> None:
    """
    Remove files from the repository or staging area.
    
    :param files: List of file paths to remove.
    :param local_path: Local path of the repository.
    :param cached: Only remove from staging area (keep in working directory).
    """
    try:
        repo = Repo(local_path)
        remove_files(repo, files, cached)
        action = "staged" if cached else "working tree"
        print(f"Removed [yellow]{', '.join(files)}[/yellow] from {action}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("untracked")
def show_untracked_files(
    local_path: str = "."
) -> None:
    """
    Show untracked files in the repository.
    
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        untracked = get_untracked_files(repo)
        if untracked:
            print("Untracked files:")
            for file in untracked:
                print(f"  [red]{file}[/red]")
        else:
            print("No untracked files.")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("tag")
def create_tag_cmd(
    tag_name: str,
    commit_ref: str = "HEAD",
    message: Optional[str] = None,
    local_path: str = ".",
) -> None:
    """
    Create a new tag.
    
    :param tag_name: Name of the tag to create.
    :param commit_ref: Reference to the commit to tag.
    :param message: Optional message for annotated tag.
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        create_tag(repo, tag_name, commit_ref, message)
        tag_type = "annotated" if message else "lightweight"
        print(f"Created {tag_type} tag [bold]{tag_name}[/bold] at {commit_ref}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("list-tags")
def list_all_tags(
    local_path: str = "."
) -> None:
    """
    List all tags in the repository.
    
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        tags = list_tags(repo)
        if tags:
            print("Tags:")
            for tag in sorted(tags):
                print(f"  [cyan]{tag}[/cyan]")
        else:
            print("No tags found.")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("delete-tag")
def delete_tag_cmd(
    tag_name: str,
    local_path: str = ".",
) -> None:
    """
    Delete a tag from the repository.
    
    :param tag_name: Name of the tag to delete.
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        delete_tag(repo, tag_name)
        print(f"Deleted tag [bold]{tag_name}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("stash")
def stash_changes_cmd(
    message: Optional[str] = None,
    include_untracked: bool = False,
    local_path: str = ".",
) -> None:
    """
    Stash changes in the working directory.
    
    :param message: Optional message for the stash.
    :param include_untracked: Include untracked files in stash.
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        stash_changes(repo, message, include_untracked)
        print(f"Stashed changes with message: [bold]{message or 'WIP'}[/bold]")
    except GitError as e:
        print(f"[red]Error:[/red] {e}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("stash-pop")
def pop_stash_cmd(
    stash_ref: str = "stash@{0}",
    local_path: str = ".",
) -> None:
    """
    Apply and remove the most recent stash.
    
    :param stash_ref: Reference to specific stash entry.
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        stash_pop(repo, stash_ref)
        print(f"Applied and removed stash [bold]{stash_ref}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("list-stashes")
def list_all_stashes(
    local_path: str = "."
) -> None:
    """
    List all stashes in the repository.
    
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        stashes = list_stashes(repo)
        if stashes:
            print("Stashes:")
            for stash in stashes:
                print(f"  [yellow]{stash}[/yellow]")
        else:
            print("No stashes found.")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("merge")
def merge_branch_cmd(
    branch_name: str,
    no_ff: bool = False,
    local_path: str = ".",
) -> None:
    """
    Merge a branch into the current branch.
    
    :param branch_name: Name of the branch to merge.
    :param no_ff: Force a merge commit (no fast-forward).
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        merge_branch(repo, branch_name, no_ff)
        merge_type = "no-fast-forward" if no_ff else "fast-forward"
        print(f"Merged branch [bold]{branch_name}[/bold] ({merge_type})")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("rebase")
def rebase_branch_cmd(
    branch_name: str,
    interactive: bool = False,
    local_path: str = ".",
) -> None:
    """
    Rebase current branch onto another branch.
    
    :param branch_name: Name of the branch to rebase onto.
    :param interactive: Perform interactive rebase.
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        rebase_branch(repo, branch_name, interactive)
        rebase_type = "interactive" if interactive else "standard"
        print(f"Rebased onto [bold]{branch_name}[/bold] ({rebase_type})")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("cherry-pick")
def cherry_pick_cmd(
    commit_ref: str,
    local_path: str = ".",
) -> None:
    """
    Cherry-pick a specific commit onto the current branch.
    
    :param commit_ref: Reference to the commit to cherry-pick.
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        cherry_pick(repo, commit_ref)
        print(f"Cherry-picked commit [bold]{commit_ref}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("blame")
def blame_file_cmd(
    file_path: str,
    local_path: str = ".",
) -> None:
    """
    Show what revision and author last modified each line of a file.
    
    :param file_path: Path to the file to blame.
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        blame_data = blame_file(repo, file_path)
        
        print(f"Blame for [bold]{blame_data['file_path']}[/bold]:")
        print()
        
        # Display blame information in a table format
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Line", style="dim", width=4)
        table.add_column("Commit", style="yellow", width=8)
        table.add_column("Author", style="cyan", width=20)
        table.add_column("Date", style="green", width=12)
        table.add_column("Content", style="white")
        
        for line_info in blame_data['lines']:
            table.add_row(
                str(line_info['line_number']),
                line_info['commit_hash'][:7],
                line_info['author_name'],
                line_info['author_date'],
                line_info['content']
            )
        
        console.print(table)
        
    except GitError as e:
        print(f"[red]Error:[/red] {e}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("remotes")
def list_remotes(
    local_path: str = "."
) -> None:
    """
    List all remote repositories.
    
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        remotes = get_remote_repos(repo)
        if remotes:
            print("Remote repositories:")
            for remote_url in remotes:
                print(f"  [cyan]{remote_url}[/cyan]")
        else:
            print("No remote repositories found.")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("clone")
def clone_from_repo(
    repo_url: str,
    local_path: str = ".",
) -> None:
    """
    Clone a Git repository from the given URL to the specified local path.
    
    :param repo_url: URL of the repository to clone.
    :param local_path: Local path where the repository should be cloned (default is current directory).
    """
    try:
        clone_repo(repo_url, local_path)
        print(f"Repository cloned from [blue]{repo_url}[/blue] to [green]{local_path}[/green].")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("pull")
def pull_from_repo(
    local_path: str = ".",
    remote_name: str = "origin",
    branch_name: str = "main",
    rebase: bool = False,
) -> None:
    """
    Pull changes from the specified remote repository and branch into the local repository.
    
    :param local_path: Local path of the repository to pull changes into.
    :param remote_name: Name of the remote repository (default is 'origin').
    :param branch_name: Name of the branch to pull from (default is 'main').
    :param rebase: Whether to rebase instead of merge when pulling.
    """
    try:
        repo = Repo(local_path)
        result = pull_changes(repo, remote_name, branch_name, rebase)
        print(f"[blue]{result}[/blue]")
        
        if rebase:
            print("[cyan]Changes were rebased instead of merged[/cyan]")
            
    except GitError as e:
        print(f"[red]Error:[/red] {e}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("push")
def push_to_repo(
    local_path: str = ".",
    remote_name: str = "origin",
    branch_name: str = "main",
    force: bool = False,
    set_upstream: bool = False,
) -> None:
    """
    Push committed changes to the specified remote repository and branch.
    
    :param local_path: Local path of the repository to push changes from.
    :param remote_name: Name of the remote repository (default is 'origin').
    :param branch_name: Name of the branch to push to (default is 'main').
    :param force: Whether to force push (use with caution).
    :param set_upstream: Whether to set up tracking relationship.
    """
    try:
        repo = Repo(local_path)
        result = push_changes(repo, remote_name, branch_name, force, set_upstream)
        print(f"[green]{result}[/green]")
        
        if force:
            print("[yellow]Warning: Force push was used. This can be dangerous![/yellow]")
        if set_upstream:
            print(f"[cyan]Upstream tracking set to {remote_name}/{branch_name}[/cyan]")
            
    except GitError as e:
        print(f"[red]Error:[/red] {e}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("status")
def get_repo_status_cmd(
    local_path: str = ".",
    show_gript_info: bool = True,
) -> None:
    """
    Get enhanced status of the repository including DotGript automation info.
    
    :param local_path: Local path of the repository to check status.
    :param show_gript_info: Whether to show DotGript automation information.
    """
    try:
        # Try to use enhanced status if .gript exists
        try:
            comprehensive_status = get_gript_status(local_path)
            status = comprehensive_status['git_status']
            gript_info = comprehensive_status['gript_info']
            automation_enabled = comprehensive_status['automation_enabled']
        except Exception:
            # Fallback to basic status
            repo = Repo(local_path)
            status = get_repo_status(repo)
            gript_info = None
            automation_enabled = False
        
        current_branch = get_current_branch(Repo(local_path))
        print(f"On branch [bold green]{current_branch}[/bold green]")
        
        # Show DotGript automation status
        if show_gript_info and gript_info:
            if automation_enabled:
                print("🤖 [bold cyan]DotGript automation:[/bold cyan] [green]enabled[/green]")
                if gript_info.get('stats'):
                    last_op = gript_info['stats'].get('last_operation')
                    if last_op:
                        print(f"   📊 Last operation: [yellow]{last_op}[/yellow]")
                
                # Show active features if available
                if status.get('active_features'):
                    active_count = len(status['active_features'])
                    print(f"   🌟 Active feature branches: [cyan]{active_count}[/cyan]")
            else:
                print("💤 [bold yellow]DotGript automation:[/bold yellow] [red]not configured[/red]")
                print("   💡 Run [blue]gript init --setup-gript[/blue] to enable automation")
        print()
        
        # Show staged changes
        if status['staged']:
            print("[bold green]Changes to be committed:[/bold green]")
            for file_status in status['staged']:
                print(f"  [green]{file_status}[/green]")
            print()
        
        # Show renamed files
        if status['renamed']:
            print("[bold yellow]Renamed files:[/bold yellow]")
            for file_status in status['renamed']:
                print(f"  [yellow]{file_status}[/yellow]")
            print()
        
        # Show modified files
        if status['modified']:
            print("[bold red]Changes not staged for commit:[/bold red]")
            for file_path in status['modified']:
                print(f"  [red]modified:   {file_path}[/red]")
            print()
        
        # Show deleted files
        if status['deleted']:
            print("[bold red]Deleted files:[/bold red]")
            for file_path in status['deleted']:
                print(f"  [red]deleted:    {file_path}[/red]")
            print()
        
        # Show untracked files
        if status['untracked']:
            print("[bold red]Untracked files:[/bold red]")
            for file_path in status['untracked']:
                print(f"  [red]{file_path}[/red]")
            print()
        
        # Show conflicts
        if status.get('conflicts'):
            print("[bold magenta]Merge conflicts:[/bold magenta]")
            for file_path in status['conflicts']:
                print(f"  [magenta]{file_path}[/magenta]")
            print()
        
        # Status summary
        status_values = [v for k, v in status.items() if k != 'active_features']
        if not any(status_values):
            print("[green]Working tree clean[/green]")
            
    except GitError as e:
        print(f"[red]Error:[/red] {e}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("commit")
def commit_changes_cmd(
    local_path: str = ".",
    message: str = "Commit changes",
    files: Optional[List[str]] = None,
    amend: bool = False,
    allow_empty: bool = False,
    use_conventional: bool = True,
) -> None:
    """
    Enhanced commit with DotGript automation features and tracking.
    
    :param local_path: Local path of the repository to commit changes to.
    :param message: Commit message.
    :param files: Optional list of files to commit. If None, all changes will be committed.
    :param amend: Whether to amend the last commit instead of creating a new one.
    :param allow_empty: Whether to allow empty commits.
    :param use_conventional: Whether to use conventional commit formatting and validation.
    """
    try:
        # Always use GriptGit for enhanced tracking
        gript_git = GriptGit(local_path)
        result = gript_git.commit_changes(
            message=message,
            files=files,
            amend=amend,
            allow_empty=allow_empty,
            use_conventional_commits=use_conventional
        )
        
        if isinstance(result, str):  # Commit hash returned from basic commit
            print("✅ [green]Commit successful![/green]")
            print(f"📝 Message: [bold]{message}[/bold]")
            print(f"🔖 Hash: [yellow]{result[:8]}[/yellow]")
            print("📊 [cyan]Operation logged to .gript/logs/[/cyan]")
        elif isinstance(result, dict) and result.get('success'):
            print("✨ [green]Smart commit successful![/green]")
            print(f"📝 Message: [bold]{result.get('message', message)}[/bold]")
            print(f"🔖 Hash: [yellow]{result.get('commit_hash', '')[:8]}[/yellow]")
            if use_conventional and result.get('conventional'):
                print("🎯 [green]Conventional commit format applied[/green]")
            print("📊 [cyan]Operation logged to .gript/logs/[/cyan]")
        else:
            error_msg = result.get('error', 'Unknown error') if isinstance(result, dict) else 'Unknown error'
            print(f"❌ [red]Commit failed:[/red] {error_msg}")
        
    except GitError as e:
        print(f"[red]Error:[/red] {e}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("info")
def get_repo_info_cmd(
    local_path: str = "."
) -> None:
    """
    Get information about the repository, including its URL and branch.
    
    :param local_path: Local path of the repository to get information from.
    """
    try:
        repo = Repo(local_path)
        info = get_repo_info(repo)
        print(f"Repository info: [bold]{info}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("branches")
def branch_cmd(
    local_path: str = "."
) -> None:
    """
    Get information about the branches in the repository.
    
    :param local_path: Local path of the repository to get branch information from.
    """
    try:
        repo = Repo(local_path)
        branches = list_branches(repo)
        current_branch = get_current_branch(repo)
        print(f"Branches: [bold]{branches}[/bold]")
        print(f"Current branch: [bold green]{current_branch}[/bold green]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("checkout")
def checkout_branch_cmd(
    branch_name: str,
    local_path: str = ".",
) -> None:
    """
    Check out a specific branch in the repository.
    
    :param branch_name: Name of the branch to check out.
    :param local_path: Local path of the repository to check out the branch in.
    """
    try:
        repo = Repo(local_path)
        checkout_branch(repo, branch_name)
        print(f"Checked out branch: [bold]{branch_name}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("create-branch")
def create_branch_cmd(
    branch_name: str,
    local_path: str = ".",
    issue_number: Optional[int] = None,
    from_branch: Optional[str] = None,
) -> None:
    """
    Create a new branch in the repository with enhanced tracking.
    
    :param branch_name: Name of the new branch to create.
    :param local_path: Local path of the repository to create the branch in.
    :param issue_number: Optional issue number for tracking.
    :param from_branch: Base branch to create from.
    """
    try:
        # Use GriptGit for enhanced tracking
        gript_git = GriptGit(local_path)
        result = gript_git.create_branch(branch_name, issue_number, from_branch)
        
        if result.get('success'):
            print(f"✅ [green]Created new branch:[/green] [bold]{result['branch_name']}[/bold]")
            if issue_number:
                print(f"🎯 [blue]Linked to issue #{issue_number}[/blue]")
            if result.get('base_branch'):
                print(f"📍 [yellow]Based on: {result['base_branch']}[/yellow]")
        else:
            print(f"❌ [red]Failed to create branch:[/red] {result.get('error')}")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("remove-branch")
def remove_branch_cmd(
    branch_name: str,
    local_path: str = ".",
) -> None:
    """
    Remove a branch from the repository.
    
    :param branch_name: Name of the branch to remove.
    :param local_path: Local path of the repository to remove the branch from.
    """
    try:
        repo = Repo(local_path)
        remove_branch(repo, branch_name)
        print(f"Removed branch: [bold]{branch_name}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("add-remote")
def add_remote_cmd(
    remote_name: str,
    remote_url: str,
    local_path: str = ".",
) -> None:
    """
    Add a new remote repository to the local repository.
    
    :param remote_name: Name of the new remote repository.
    :param remote_url: URL of the new remote repository.
    :param local_path: Local path of the repository to add the remote to.
    """
    try:
        repo = Repo(local_path)
        add_remote(repo, remote_name, remote_url)
        print(f"Added remote: [bold]{remote_name}[/bold] with URL: [bold]{remote_url}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("fetch")
def fetch_remote_cmd(
    remote_name: str = "origin",
    local_path: str = ".",
) -> None:
    """
    Fetch updates from the specified remote repository.
    
    :param remote_name: Name of the remote repository to fetch from (default is 'origin').
    :param local_path: Local path of the repository to fetch updates into.
    """
    try:
        repo = Repo(local_path)
        fetch_remote(repo, remote_name)
        print(f"Fetched updates from remote: [bold]{remote_name}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("switch")
def switch_branch_cmd(
    branch_name: str,
    local_path: str = ".",
) -> None:
    """
    Switch to a different branch in the repository.
    
    :param branch_name: Name of the branch to switch to.
    :param local_path: Local path of the repository to switch branches in.
    """
    try:
        repo = Repo(local_path)
        switch_branch(repo, branch_name)
        print(f"Switched to branch: [bold]{branch_name}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


# Enhanced DotGript automation commands
@app.command("setup-automation")
def setup_automation_cmd(
    local_path: str = ".",
    workflow: str = "github_flow",
    enforce_conventional_commits: bool = True,
    auto_squash_merge: bool = True,
) -> None:
    """
    Setup DotGript automation for an existing repository.
    
    :param local_path: Local path of the repository.
    :param workflow: Workflow type (github_flow, gitflow, gitlab_flow, custom).
    :param enforce_conventional_commits: Whether to enforce conventional commits.
    :param auto_squash_merge: Whether to enable auto squash merge.
    """
    try:
        setup_gript_automation(
            local_path, workflow, enforce_conventional_commits, auto_squash_merge
        )
        
        print("✨ [bold green]DotGript automation configured![/bold green]")
        print(f"🔧 Workflow: [cyan]{workflow}[/cyan]")
        print(f"📝 Conventional commits: [{'green' if enforce_conventional_commits else 'red'}]{'enabled' if enforce_conventional_commits else 'disabled'}[/]")
        print(f"🔄 Auto squash merge: [{'green' if auto_squash_merge else 'red'}]{'enabled' if auto_squash_merge else 'disabled'}[/]")
        print("📁 Created [blue].gript/[/blue] folder with automation configs")
        print("🎯 Features enabled: operation logging, statistics tracking, branch metadata")
        
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@app.command("gript-status")
def gript_status_cmd(
    local_path: str = "."
) -> None:
    """
    Show comprehensive DotGript automation status and statistics.
    
    :param local_path: Local path of the repository.
    """
    try:
        comprehensive_status = get_gript_status(local_path)
        
        print("[bold cyan]🤖 DotGript Automation Status[/bold cyan]")
        print("=" * 40)
        
        # Git status
        git_status = comprehensive_status['git_status']
        current_branch = comprehensive_status['current_branch']
        print(f"📍 Current branch: [bold green]{current_branch}[/bold green]")
        
        # Automation status
        automation_enabled = comprehensive_status['automation_enabled']
        if automation_enabled:
            print("🎯 Automation: [bold green]enabled[/bold green]")
        else:
            print("⚠️  Automation: [bold red]not configured[/bold red]")
            print("💡 Run [blue]gript setup-automation[/blue] to enable")
            return
        
        # DotGript info
        gript_info = comprehensive_status['gript_info']
        if gript_info.get('stats'):
            print("\n📊 [bold]Statistics:[/bold]")
            stats = gript_info['stats']
            for operation, count in stats.items():
                if operation != 'last_operation' and isinstance(count, int):
                    print(f"   {operation}: [cyan]{count}[/cyan]")
            
            if stats.get('last_operation'):
                print(f"   last operation: [yellow]{stats['last_operation']}[/yellow]")
        
        # Recent operations
        if gript_info.get('recent_operations'):
            print("\n🕒 [bold]Recent Operations (today):[/bold]")
            for op in gript_info['recent_operations'][-5:]:  # Show last 5
                timestamp = op['timestamp'][:19].replace('T', ' ')
                print(f"   [dim]{timestamp}[/dim] {op['operation']}")
        
        # Active features
        if git_status.get('active_features'):
            print(f"\n🌟 [bold]Active Feature Branches:[/bold] [cyan]{len(git_status['active_features'])}[/cyan]")
            for feature in git_status['active_features']:
                print(f"   • [green]{feature}[/green]")
        
        # Config info
        if gript_info.get('config_exists'):
            print("\n⚙️  [bold]Configuration:[/bold] [green]loaded[/green]")
            print(f"   📁 Config directory: [blue]{gript_info['gript_dir']}[/blue]")
        
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@app.command("migrate-to-gript")
def migrate_repository_cmd(
    local_path: str = "."
) -> None:
    """
    Migrate an existing Git repository to use DotGript automation with comprehensive data migration.
    
    :param local_path: Local path of the repository.
    """
    try:
        print("🔄 [yellow]Starting DotGript migration...[/yellow]")
        result = migrate_to_gript(local_path)
        
        if result['success']:
            print("🎉 [bold green]Migration successful![/bold green]")
            print(f"📁 DotGript directory: [blue]{result['gript_dir']}[/blue]")
            
            # Show migration statistics if available
            if 'migration_results' in result:
                migration_results = result['migration_results']
                print("\n📊 [bold]Migration Results:[/bold]")
                print(f"   🌿 Branches migrated: [cyan]{migration_results.get('branches_migrated', 0)}[/cyan]")
                print(f"   📝 Recent commits analyzed: [cyan]{migration_results.get('commits_analyzed', 0)}[/cyan]")
                print(f"   🔗 Remotes tracked: [cyan]{migration_results.get('remotes_tracked', 0)}[/cyan]")
                print(f"   🏷️  Tags migrated: [cyan]{migration_results.get('tags_migrated', 0)}[/cyan]")
            
            print("\n✨ [bold]Features enabled:[/bold]")
            for feature in result['features_enabled']:
                print(f"   • [green]{feature.replace('_', ' ').title()}[/green]")
            
            print("\n💡 [dim]Migration completed - Use 'gript git automation-status' for details[/dim]")
            print("💡 [dim]Try 'gript git smart-feature-start <name>' for smart branch creation[/dim]")
        else:
            print(f"❌ [bold red]Migration failed:[/bold red] {result['error']}")
            print(f"💬 {result['message']}")
            
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@app.command("smart-commit")
def smart_commit_cmd(
    local_path: str = ".",
    message: Optional[str] = None,
    auto_suggest: bool = False,
) -> None:
    """
    Enhanced smart commit with AI suggestions and conventional commit formatting.
    
    :param local_path: Local path of the repository.
    :param message: Commit message (if None, will use AI suggestions).
    :param auto_suggest: Whether to show AI-powered commit suggestions.
    """
    try:
        gript_git = create_gript_git(local_path)
        
        if auto_suggest or message is None:
            print("🤖 [bold cyan]AI-powered commit suggestions:[/bold cyan]")
            suggestions = gript_git.automation.intelligent_commit_suggestions()
            
            if not suggestions:
                print("❌ No changes detected for commit suggestions")
                return
            
            # Show suggestions
            table = Table(title="Smart Commit Suggestions")
            table.add_column("#", justify="right", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Files", justify="right", style="blue")
            table.add_column("Message", style="green")
            table.add_column("Confidence", justify="right", style="magenta")
            
            for idx, suggestion in enumerate(suggestions[:5], 1):  # Show top 5
                table.add_row(
                    str(idx),
                    suggestion['suggested_commit_type'].value,
                    str(len(suggestion['files'])),
                    suggestion['suggested_messages'][0][:50] + "..." if len(suggestion['suggested_messages'][0]) > 50 else suggestion['suggested_messages'][0],
                    f"{suggestion['confidence']:.2f}"
                )
            
            console.print(table)
            
            if message is None:
                # Use the first suggestion
                selected = suggestions[0]
                message = selected['suggested_messages'][0]
                files = selected['files']
                commit_type = selected['suggested_commit_type']
                
                result = gript_git.automation.smart_commit(
                    message=message,
                    files=files,
                    commit_type=commit_type,
                    auto_stage=True
                )
                
                if result.get('success'):
                    print("\n✨ [bold green]Smart commit successful![/bold green]")
                    print(f"📝 Message: [bold]{result['message']}[/bold]")
                    print(f"🔖 Hash: [yellow]{result['short_sha']}[/yellow]")
                    print(f"📊 Changes: {result['insertions']} insertions (+), {result['deletions']} deletions (-)")
                else:
                    print(f"❌ [red]Smart commit failed:[/red] {result.get('error')}")
        else:
            # Use provided message with smart formatting
            result = gript_git.commit_changes(message=message, use_conventional_commits=True)
            
            if isinstance(result, dict) and result.get('success'):
                print("✨ [bold green]Smart commit successful![/bold green]")
                print(f"📝 Message: [bold]{result.get('message', message)}[/bold]")
                print(f"🔖 Hash: [yellow]{result.get('commit_hash', '')[:7]}[/yellow]")
            else:
                error_msg = result.get('error', 'Unknown error') if isinstance(result, dict) else str(result)
                print(f"❌ [red]Smart commit failed:[/red] {error_msg}")
            
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


# =====================================================================
# AUTOMATION COMMANDS - DotGript Smart Git Workflows
# =====================================================================

@app.command("smart-feature-start")
def smart_feature_start_cmd(
    feature_name: str,
    local_path: str = ".",
    issue_number: Optional[int] = None,
    from_branch: Optional[str] = None,
    interactive: bool = False,
) -> None:
    """
    Start a new feature branch with smart automation and metadata tracking.
    
    :param feature_name: Name of the feature to create
    :param local_path: Local path of the repository
    :param issue_number: Optional issue number for tracking
    :param from_branch: Base branch to create from
    :param interactive: Whether to use interactive naming
    """
    try:
        gript_git = GriptGit(local_path)
        
        if hasattr(gript_git.automation, 'smart_feature_start'):
            result = gript_git.automation.smart_feature_start(
                feature_name=feature_name,
                issue_number=issue_number,
                from_branch=from_branch,
                interactive=interactive
            )
            
            if result.get('success'):
                print("🌟 [bold green]Smart feature branch created successfully![/bold green]")
                print(f"🌿 Branch: [bold cyan]{result['branch_name']}[/bold cyan]")
                print(f"📍 Base: [yellow]{result['base_branch']}[/yellow]")
                print(f"🔗 Upstream: {'Set' if result.get('upstream_set') else 'Not set'}")
                if issue_number:
                    print(f"🎯 Issue: [blue]#{issue_number}[/blue]")
                print(f"⏰ Created: {result['created_at']}")
            else:
                print(f"❌ [red]Failed to create feature branch:[/red] {result.get('error')}")
        else:
            # Fallback to basic branch creation
            result = gript_git.create_branch(feature_name, issue_number, from_branch, interactive)
            print(f"✅ [green]Feature branch created:[/green] [bold]{result['branch_name']}[/bold]")
            
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@app.command("smart-feature-finish")
def smart_feature_finish_cmd(
    local_path: str = ".",
    branch_name: Optional[str] = None,
    squash: Optional[bool] = None,
    delete_branch: Optional[bool] = None,
    push_after_merge: bool = True,
) -> None:
    """
    Finish a feature branch with smart automation (merge and cleanup).
    
    :param local_path: Local path of the repository
    :param branch_name: Branch to finish (current branch if None)
    :param squash: Whether to squash merge
    :param delete_branch: Whether to delete branch after merge
    :param push_after_merge: Whether to push after merge
    """
    try:
        gript_git = GriptGit(local_path)
        
        if hasattr(gript_git.automation, 'smart_feature_finish'):
            result = gript_git.automation.smart_feature_finish(
                branch_name=branch_name,
                squash=squash,
                delete_branch=delete_branch,
                push_after_merge=push_after_merge
            )
            
            if result.get('success', True):
                print("🎉 [bold green]Feature finished successfully![/bold green]")
                print(f"🌿 Branch: [bold]{result['branch']}[/bold]")
                print(f"🎯 Target: [yellow]{result['target']}[/yellow]")
                print(f"📝 Squashed: {'Yes' if result.get('squashed') else 'No'}")
                print(f"📊 Commits merged: {len(result.get('commits_merged', []))}")
                print(f"⏰ Completed: {result.get('timestamp')}")
            else:
                print(f"❌ [red]Failed to finish feature:[/red] {result.get('error')}")
        else:
            print("❌ [red]Smart feature finish not available. Use regular merge commands.[/red]")
            
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@app.command("list-active-features")
def list_active_features_cmd(
    local_path: str = "."
) -> None:
    """
    List all active feature branches with metadata and status.
    
    :param local_path: Local path of the repository
    """
    try:
        gript_git = GriptGit(local_path)
        
        if hasattr(gript_git.automation, 'list_active_features'):
            features = gript_git.automation.list_active_features()
            
            if features:
                table = Table(title="🌿 Active Feature Branches", show_header=True, header_style="bold magenta")
                table.add_column("Branch", style="cyan", no_wrap=True)
                table.add_column("Type", style="green")
                table.add_column("Issue", style="blue")
                table.add_column("Last Commit", style="yellow")
                table.add_column("Status", style="white")
                
                for feature in features:
                    branch_name = feature.get('name', 'unknown')
                    branch_type = feature.get('type', 'unknown')
                    issue = f"#{feature['issue_number']}" if feature.get('issue_number') else '-'
                    last_commit = feature.get('last_commit_date', 'unknown')[:10]  # Date only
                    status = "🟢 Active" if feature.get('is_current') else "⚪ Inactive"
                    
                    table.add_row(branch_name, branch_type, issue, last_commit, status)
                
                console.print(table)
            else:
                print("📭 [yellow]No active feature branches found.[/yellow]")
        else:
            print("❌ [red]Smart feature listing not available.[/red]")
            
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@app.command("commit-suggestions")
def commit_suggestions_cmd(
    local_path: str = "."
) -> None:
    """
    Get AI-powered commit message suggestions based on staged changes.
    
    :param local_path: Local path of the repository
    """
    try:
        gript_git = GriptGit(local_path)
        
        if hasattr(gript_git.automation, 'intelligent_commit_suggestions'):
            suggestions = gript_git.automation.intelligent_commit_suggestions()
            
            if suggestions:
                print("🤖 [bold cyan]AI Commit Suggestions:[/bold cyan]\n")
                
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("#", style="dim", width=3)
                table.add_column("Type", style="green", width=10)
                table.add_column("Message", style="white")
                table.add_column("Files", style="yellow", width=15)
                table.add_column("Confidence", style="blue", width=10)
                
                for i, suggestion in enumerate(suggestions, 1):
                    files_str = ", ".join(suggestion.get('files', [])[:2])
                    if len(suggestion.get('files', [])) > 2:
                        files_str += f" +{len(suggestion['files'])-2} more"
                    
                    confidence = f"{suggestion.get('confidence', 0)*100:.0f}%"
                    
                    table.add_row(
                        str(i),
                        suggestion.get('suggested_commit_type', 'unknown'),
                        suggestion.get('suggested_message', ''),
                        files_str,
                        confidence
                    )
                
                console.print(table)
                print("\n💡 [dim]Use 'gript git smart-commit' to select and apply a suggestion.[/dim]")
            else:
                print("📭 [yellow]No commit suggestions available. Make sure you have staged changes.[/yellow]")
        else:
            print("❌ [red]Commit suggestions not available.[/red]")
            
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@app.command("smart-release")
def smart_release_cmd(
    local_path: str = ".",
    version_bump: str = "patch",
    pre_release: bool = False,
    release_notes: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """
    Create a smart release with automated versioning and changelog generation.
    
    :param local_path: Local path of the repository
    :param version_bump: Version bump type (patch, minor, major)
    :param pre_release: Whether this is a pre-release
    :param release_notes: Optional custom release notes
    :param dry_run: Whether to perform a dry run
    """
    try:
        gript_git = GriptGit(local_path)
        
        if hasattr(gript_git.automation, 'smart_release'):
            result = gript_git.automation.smart_release(
                version_bump=version_bump,
                pre_release=pre_release,
                release_notes=release_notes,
                dry_run=dry_run
            )
            
            if result.get('success'):
                action = "Would create" if dry_run else "Created"
                print(f"🚀 [bold green]{action} release successfully![/bold green]")
                print(f"🏷️  Version: [bold]{result['version']}[/bold]")
                print(f"📦 Tag: [yellow]{result.get('tag')}[/yellow]")
                print(f"📋 Changelog: {'Generated' if result.get('changelog_updated') else 'Skipped'}")
                
                if result.get('changelog_preview'):
                    print("\n📄 [bold]Changelog Preview:[/bold]")
                    print(result['changelog_preview'])
            else:
                print(f"❌ [red]Failed to create release:[/red] {result.get('error')}")
        else:
            print("❌ [red]Smart release not available.[/red]")
            
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@app.command("hotfix-start")
def hotfix_start_cmd(
    hotfix_name: str,
    local_path: str = ".",
    target_version: Optional[str] = None,
    from_tag: Optional[str] = None,
) -> None:
    """
    Start a hotfix workflow for urgent fixes.
    
    :param hotfix_name: Name of the hotfix
    :param local_path: Local path of the repository
    :param target_version: Target version for the hotfix
    :param from_tag: Tag to create hotfix from
    """
    try:
        gript_git = GriptGit(local_path)
        
        if hasattr(gript_git.automation, 'hotfix_workflow'):
            result = gript_git.automation.hotfix_workflow(
                hotfix_name=hotfix_name,
                target_version=target_version,
                from_tag=from_tag
            )
            
            if result.get('success'):
                print("🚨 [bold red]Hotfix started successfully![/bold red]")
                print(f"🩹 Branch: [bold]{result['hotfix_branch']}[/bold]")
                print(f"🏷️  Target Version: [yellow]{result.get('target_version')}[/yellow]")
                print(f"📍 Base: {result.get('base_commit', 'latest')}")
            else:
                print(f"❌ [red]Failed to start hotfix:[/red] {result.get('error')}")
        else:
            print("❌ [red]Hotfix workflow not available.[/red]")
            
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@app.command("hotfix-finish")
def hotfix_finish_cmd(
    local_path: str = ".",
    hotfix_branch: Optional[str] = None,
) -> None:
    """
    Finish a hotfix workflow (merge to main and develop).
    
    :param local_path: Local path of the repository
    :param hotfix_branch: Hotfix branch to finish (current if None)
    """
    try:
        gript_git = GriptGit(local_path)
        
        if hasattr(gript_git.automation, 'finish_hotfix'):
            result = gript_git.automation.finish_hotfix(hotfix_branch=hotfix_branch)
            
            if result.get('success'):
                print("✅ [bold green]Hotfix finished successfully![/bold green]")
                print(f"🩹 Branch: [bold]{result['hotfix_branch']}[/bold]")
                print(f"🎯 Merged to: {', '.join(result.get('merged_to', []))}")
                print(f"🏷️  Version: [yellow]{result.get('version')}[/yellow]")
            else:
                print(f"❌ [red]Failed to finish hotfix:[/red] {result.get('error')}")
        else:
            print("❌ [red]Hotfix finish not available.[/red]")
            
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@app.command("automation-status")
def automation_status_cmd(
    local_path: str = "."
) -> None:
    """
    Show comprehensive automation status and configuration.
    
    :param local_path: Local path of the repository
    """
    try:
        gript_git = GriptGit(local_path)
        
        # Get automation config
        if hasattr(gript_git.automation, 'config'):
            config = gript_git.automation.config
            print("⚙️  [bold cyan]DotGript Automation Status[/bold cyan]\n")
            
            # Configuration table
            config_table = Table(title="Configuration", show_header=False, box=None)
            config_table.add_column("Setting", style="bold cyan")
            config_table.add_column("Value", style="white")
            
            config_table.add_row("Workflow Type", config.workflow_type.value)
            config_table.add_row("Main Branch", config.branch_strategy.main_branch)
            config_table.add_row("Develop Branch", config.branch_strategy.develop_branch)
            config_table.add_row("Conventional Commits", "✅ Enabled" if config.enforce_conventional_commits else "❌ Disabled")
            config_table.add_row("Auto Squash Merge", "✅ Enabled" if config.auto_squash_merge else "❌ Disabled")
            config_table.add_row("Semantic Versioning", "✅ Enabled" if config.semantic_versioning else "❌ Disabled")
            config_table.add_row("Auto Changelog", "✅ Enabled" if config.auto_changelog else "❌ Disabled")
            
            console.print(config_table)
            print()
            
            # Protected branches
            if config.protected_branches:
                print("🛡️  [bold]Protected Branches:[/bold]")
                for branch in config.protected_branches:
                    print(f"   • [yellow]{branch}[/yellow]")
                print()
        
        # Get gript status
        status = get_gript_status(local_path)
        
        # Statistics
        if status.get('gript_info', {}).get('stats'):
            stats = status['gript_info']['stats']
            stats_table = Table(title="📊 Operation Statistics", show_header=True, header_style="bold magenta")
            stats_table.add_column("Operation", style="cyan")
            stats_table.add_column("Count", style="green")
            
            for operation, count in stats.items():
                if operation != 'last_operation':
                    stats_table.add_row(operation.replace('_', ' ').title(), str(count))
            
            console.print(stats_table)
            print()
        
        print(f"📁 [bold]Gript Directory:[/bold] {status.get('gript_info', {}).get('gript_dir', 'N/A')}")
        print(f"🌿 [bold]Current Branch:[/bold] {status.get('current_branch', 'N/A')}")
        print(f"🤖 [bold]Automation:[/bold] {'✅ Enabled' if status.get('automation_enabled') else '❌ Disabled'}")
        
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
