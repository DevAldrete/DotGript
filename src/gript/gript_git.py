from typer import Typer
from gript.core.gript_git import (
    clone_repo, commit_changes, get_repo_info, push_changes, pull_changes, 
    get_repo_status, checkout_branch, switch_branch, remove_branch, add_remote, 
    create_branch, get_current_branch, get_remote_repos, fetch_remote, list_branches,
    get_git_log, show_commit, get_diff, reset_repo, create_tag, list_tags, delete_tag,
    stash_changes, stash_pop, list_stashes, merge_branch, rebase_branch, cherry_pick,
    init_repo, get_untracked_files, add_files, remove_files, get_file_content, blame_file
)
from git import Repo, GitCommandError
from typing import Optional, List
from rich import print
from rich.console import Console
from rich.syntax import Syntax

app = Typer()
console = Console()

@app.command("init")
def init_repository(
    path: str = ".",
    bare: bool = False,
) -> None:
    """
    Initialize a new Git repository.
    
    :param path: Path where to initialize the repository (default is current directory).
    :param bare: Whether to create a bare repository.
    """
    try:
        repo = init_repo(path, bare)
        if bare:
            print(f"Initialized empty [yellow]bare[/yellow] Git repository in [green]{repo.git_dir}[/green]")
        else:
            print(f"Initialized empty Git repository in [green]{repo.git_dir}[/green]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("log")
def get_log(
    local_path: str = ".",
    max_count: int = 10,
    oneline: bool = False,
) -> None:
    """
    Show commit logs.
    
    :param local_path: Local path of the repository.
    :param max_count: Maximum number of commits to show.
    :param oneline: Format as one line per commit.
    """
    try:
        repo = Repo(local_path)
        logs = get_git_log(repo, max_count, oneline)
        for log_entry in logs:
            if oneline:
                print(log_entry)
            else:
                console.print(log_entry, style="dim")
                print()
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("show")
def show_commit_details(
    commit_ref: str = "HEAD",
    local_path: str = ".",
) -> None:
    """
    Show detailed information about a specific commit.
    
    :param commit_ref: Reference to the commit (hash, HEAD, etc.).
    :param local_path: Local path of the repository.
    """
    try:
        repo = Repo(local_path)
        commit_info = show_commit(repo, commit_ref)
        syntax = Syntax(commit_info, "diff", theme="monokai", line_numbers=False)
        console.print(syntax)
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("diff")
def show_diff(
    local_path: str = ".",
    cached: bool = False,
    commit_ref: Optional[str] = None,
) -> None:
    """
    Show changes between commits, commit and working tree, etc.
    
    :param local_path: Local path of the repository.
    :param cached: Show staged changes.
    :param commit_ref: Specific commit to diff against.
    """
    try:
        repo = Repo(local_path)
        diff_output = get_diff(repo, cached, commit_ref)
        if diff_output:
            syntax = Syntax(diff_output, "diff", theme="monokai", line_numbers=False)
            console.print(syntax)
        else:
            print("No differences found.")
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
        blame_output = blame_file(repo, file_path)
        print(f"Blame for [bold]{file_path}[/bold]:")
        for line in blame_output:
            print(f"  {line}")
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
) -> None:
    """
    Pull changes from the specified remote repository and branch into the local repository.
    
    :param local_path: Local path of the repository to pull changes into.
    :param remote_name: Name of the remote repository (default is 'origin').
    :param branch_name: Name of the branch to pull from (default is 'main').
    """
    try:
        repo = Repo(local_path)
        pull_changes(repo, remote_name, branch_name)
        print(f"Changes [blue]pulled[/blue] from {remote_name}/{branch_name}.")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("push")
def push_to_repo(
    local_path: str = ".",
    remote_name: str = "origin",
    branch_name: str = "main",
) -> None:
    """
    Push committed changes to the specified remote repository and branch.
    
    :param local_path: Local path of the repository to push changes from.
    :param remote_name: Name of the remote repository (default is 'origin').
    :param branch_name: Name of the branch to push to (default is 'main').
    """
    try:
        repo = Repo(local_path)
        push_changes(repo, remote_name, branch_name)
        print(f"Changes [green]pushed[/green] to {remote_name}/{branch_name}.")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("status")
def get_repo_status_cmd(
    local_path: str = "."
) -> None:
    """
    Get the status of the working directory of the local repository.
    
    :param local_path: Local path of the repository to check status.
    """
    try:
        repo = Repo(local_path)
        status = get_repo_status(repo)
        print(f"Repository status:\n[bold]{status}[/bold]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")

@app.command("commit")
def commit_changes_cmd(
    local_path: str = ".",
    message: str = "Commit changes",
    files: Optional[List[str]] = None,
) -> None:
    """
    Commit changes in the repository with the given message.
    
    :param local_path: Local path of the repository to commit changes to.
    :param message: Commit message.
    :param files: Optional list of files to commit. If None, all changes will be committed.
    """
    try:
        repo = Repo(local_path)
        commit_changes(repo, message, files)
        print(f"Changes [yellow]committed[/yellow] with message: [bold]{message}[/bold]")
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
) -> None:
    """
    Create a new branch in the repository.
    
    :param branch_name: Name of the new branch to create.
    :param local_path: Local path of the repository to create the branch in.
    """
    try:
        repo = Repo(local_path)
        create_branch(repo, branch_name)
        print(f"Created new branch: [bold]{branch_name}[/bold]")
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

