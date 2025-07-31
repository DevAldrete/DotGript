"""
Gript Git Module
This module provides comprehensive functionality to interact with Git repositories.
This includes cloning repositories, checking the status of the working directory,
committing changes, managing branches, handling remotes, working with tags,
and various other Git operations.
This module is designed to be used with the Gript framework and is intended to be used
as a comprehensive replacement for essential Git functionality.
"""
from git import Repo, GitCommandError, TagReference, HEAD
from typing import Optional, List, Dict, Any, Union
import os

def clone_repo(repo_url: str, dest_dir: str) -> Repo:
    """
    Clone a Git repository from the given URL to the specified destination directory.
    
    :param repo_url: URL of the repository to clone.
    :param dest_dir: Directory where the repository will be cloned.
    :return: The cloned Repo object.
    """
    try:
        return Repo.clone_from(repo_url, dest_dir)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to clone repository: {e}")
    
def get_repo_status(repo: Repo) -> str:
    """
    Get the status of the working directory of the given repository.
    
    :param repo: The Repo object to check.
    :return: A string representing the status of the working directory.
    """
    try:
        return repo.git.status()
    except GitCommandError as e:
        raise RuntimeError(f"Failed to get repository status: {e}")

def commit_changes(repo: Repo, message: str, files: Optional[List[str]] = None) -> None:
    """
    Commit changes in the repository with the given message.
    
    :param repo: The Repo object to commit changes to.
    :param message: Commit message.
    :param files: Optional list of files to commit. If None, all changes will be committed.
    """
    try:
        if files:
            repo.index.add(files)
        else:
            repo.git.add(A=True)  # Add all changes
        repo.index.commit(message)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to commit changes: {e}")

def push_changes(repo: Repo, remote_name: str = 'origin', branch_name: str = 'main') -> None:
    """
    Push committed changes to the specified remote repository and branch.
    
    :param repo: The Repo object to push changes from.
    :param remote_name: Name of the remote repository (default is 'origin').
    :param branch_name: Name of the branch to push to (default is 'main').
    """
    try:
        repo.remotes[remote_name].push(branch_name)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to push changes: {e}")
    
def pull_changes(repo: Repo, remote_name: str = 'origin', branch_name: str = 'main') -> None:
    """
    Pull changes from the specified remote repository and branch.
    
    :param repo: The Repo object to pull changes into.
    :param remote_name: Name of the remote repository (default is 'origin').
    :param branch_name: Name of the branch to pull from (default is 'main').
    """
    try:
        repo.remotes[remote_name].pull(branch_name)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to pull changes: {e}")

def get_repo_info(repo: Repo) -> str:
    """
    Get basic information about the repository.
    
    :param repo: The Repo object to get information from.
    :return: A string containing the repository's URL and current branch.
    """
    return f"Repository URL: {repo.remotes.origin.url}, Current Branch: {repo.active_branch.name}"

def list_branches(repo: Repo) -> List[str]:
    """
    List all branches in the repository.
    
    :param repo: The Repo object to list branches from.
    :return: A list of branch names.
    """
    return [branch.name for branch in repo.branches]

def checkout_branch(repo: Repo, branch_name: str) -> None:
    """
    Check out a specific branch in the repository.
    
    :param repo: The Repo object to check out the branch in.
    :param branch_name: Name of the branch to check out.
    """
    try:
        repo.git.checkout(branch_name)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to check out branch '{branch_name}': {e}")
    
def switch_branch(repo: Repo, branch_name: str) -> None:
    """
    Switch to a specific branch in the repository.
    
    :param repo: The Repo object to switch branches in.
    :param branch_name: Name of the branch to switch to.
    """
    try:
        repo.git.switch(branch_name)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to switch to branch '{branch_name}': {e}")
    
def create_branch(repo: Repo, branch_name: str) -> None:
    """
    Create a new branch in the repository.
    
    :param repo: The Repo object to create the branch in.
    :param branch_name: Name of the new branch to create.
    """
    try:
        repo.git.checkout('-b', branch_name)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to create branch '{branch_name}': {e}")
    
def remove_branch(repo: Repo, branch_name: str) -> None:
    """
    Remove a branch from the repository.
    
    :param repo: The Repo object to remove the branch from.
    :param branch_name: Name of the branch to remove.
    """
    try:
        repo.git.branch('-d', branch_name)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to remove branch '{branch_name}': {e}")

def get_current_branch(repo: Repo) -> str:
    """
    Get the name of the current branch in the repository.
    
    :param repo: The Repo object to get the current branch from.
    :return: Name of the current branch.
    """
    return repo.active_branch.name if repo.active_branch else "No active branch"

def get_remote_repos(repo: Repo) -> List[str]:
    """
    Get a list of remote repositories associated with the local repository.
    
    :param repo: The Repo object to get remote repositories from.
    :return: A list of remote repository URLs.
    """
    return [remote.url for remote in repo.remotes]

def fetch_remote(repo: Repo, remote_name: str = 'origin') -> None:
    """
    Fetch updates from the specified remote repository.
    
    :param repo: The Repo object to fetch updates into.
    :param remote_name: Name of the remote repository (default is 'origin').
    """
    try:
        repo.remotes[remote_name].fetch()
    except GitCommandError as e:
        raise RuntimeError(f"Failed to fetch from remote '{remote_name}': {e}")
    
def add_remote(repo: Repo, remote_name: str, remote_url: str) -> None:
    """
    Add a new remote repository to the local repository.
    
    :param repo: The Repo object to add the remote to.
    :param remote_name: Name of the new remote repository.
    :param remote_url: URL of the new remote repository.
    """
    try:
        repo.create_remote(remote_name, remote_url)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to add remote '{remote_name}': {e}")

def get_git_log(repo: Repo, max_count: int = 10, oneline: bool = False) -> List[str]:
    """
    Get the Git commit log.
    
    :param repo: The Repo object to get the log from.
    :param max_count: Maximum number of commits to retrieve.
    :param oneline: Whether to format as one line per commit.
    :return: List of commit information strings.
    """
    try:
        commits = list(repo.iter_commits(max_count=max_count))
        if oneline:
            return [f"{commit.hexsha[:7]} {commit.summary}" for commit in commits]
        else:
            log_entries = []
            for commit in commits:
                entry = f"commit {commit.hexsha}\n"
                entry += f"Author: {commit.author.name} <{commit.author.email}>\n"
                entry += f"Date: {commit.committed_datetime}\n\n"
                entry += f"    {commit.message}\n"
                log_entries.append(entry)
            return log_entries
    except GitCommandError as e:
        raise RuntimeError(f"Failed to get git log: {e}")

def show_commit(repo: Repo, commit_ref: str = "HEAD") -> str:
    """
    Show detailed information about a specific commit.
    
    :param repo: The Repo object to get commit info from.
    :param commit_ref: Reference to the commit (hash, HEAD, etc.).
    :return: Detailed commit information.
    """
    try:
        commit = repo.commit(commit_ref)
        info = f"commit {commit.hexsha}\n"
        info += f"Author: {commit.author.name} <{commit.author.email}>\n"
        info += f"Date: {commit.committed_datetime}\n\n"
        info += f"{commit.message}\n\n"
        
        # Show file changes
        if commit.parents:
            diffs = commit.diff(commit.parents[0])
            for diff in diffs:
                if diff.a_path:
                    info += f"diff --git a/{diff.a_path} b/{diff.b_path or diff.a_path}\n"
                    info += f"--- a/{diff.a_path}\n"
                    info += f"+++ b/{diff.b_path or diff.a_path}\n"
                    if diff.diff:
                        info += diff.diff.decode('utf-8', errors='ignore')
                    info += "\n"
        
        return info
    except GitCommandError as e:
        raise RuntimeError(f"Failed to show commit '{commit_ref}': {e}")

def get_diff(repo: Repo, cached: bool = False, commit_ref: Optional[str] = None) -> str:
    """
    Get the diff of changes in the repository.
    
    :param repo: The Repo object to get diff from.
    :param cached: Whether to show staged (cached) changes.
    :param commit_ref: Specific commit to diff against.
    :return: Diff output as string.
    """
    try:
        if commit_ref:
            # Diff against specific commit
            commit = repo.commit(commit_ref)
            diffs = repo.head.commit.diff(commit)
        elif cached:
            # Show staged changes
            diffs = repo.head.commit.diff()
        else:
            # Show unstaged changes
            diffs = repo.index.diff(None)
        
        diff_text = ""
        for diff in diffs:
            if diff.a_path:
                diff_text += f"diff --git a/{diff.a_path} b/{diff.b_path or diff.a_path}\n"
                diff_text += f"--- a/{diff.a_path}\n"
                diff_text += f"+++ b/{diff.b_path or diff.a_path}\n"
                if diff.diff:
                    diff_text += diff.diff.decode('utf-8', errors='ignore')
                diff_text += "\n"
        
        return diff_text
    except GitCommandError as e:
        raise RuntimeError(f"Failed to get diff: {e}")

def reset_repo(repo: Repo, mode: str = "mixed", commit_ref: str = "HEAD") -> None:
    """
    Reset the repository to a specific commit.
    
    :param repo: The Repo object to reset.
    :param mode: Reset mode ('soft', 'mixed', 'hard').
    :param commit_ref: Reference to reset to.
    """
    try:
        if mode == "soft":
            repo.git.reset("--soft", commit_ref)
        elif mode == "hard":
            repo.git.reset("--hard", commit_ref)
        else:  # mixed (default)
            repo.git.reset("--mixed", commit_ref)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to reset repository: {e}")

def create_tag(repo: Repo, tag_name: str, commit_ref: str = "HEAD", message: Optional[str] = None) -> None:
    """
    Create a new tag pointing to a specific commit.
    
    :param repo: The Repo object to create tag in.
    :param tag_name: Name of the tag to create.
    :param commit_ref: Reference to the commit to tag.
    :param message: Optional message for annotated tag.
    """
    try:
        commit = repo.commit(commit_ref)
        if message:
            # Create annotated tag
            repo.create_tag(tag_name, ref=commit, message=message)
        else:
            # Create lightweight tag
            repo.create_tag(tag_name, ref=commit)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to create tag '{tag_name}': {e}")

def list_tags(repo: Repo) -> List[str]:
    """
    List all tags in the repository.
    
    :param repo: The Repo object to list tags from.
    :return: List of tag names.
    """
    try:
        return [tag.name for tag in repo.tags]
    except GitCommandError as e:
        raise RuntimeError(f"Failed to list tags: {e}")

def delete_tag(repo: Repo, tag_name: str) -> None:
    """
    Delete a tag from the repository.
    
    :param repo: The Repo object to delete tag from.
    :param tag_name: Name of the tag to delete.
    """
    try:
        repo.delete_tag(tag_name)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to delete tag '{tag_name}': {e}")

def stash_changes(repo: Repo, message: Optional[str] = None, include_untracked: bool = False) -> None:
    """
    Stash current changes in the working directory.
    
    :param repo: The Repo object to stash changes in.
    :param message: Optional message for the stash.
    :param include_untracked: Whether to include untracked files.
    """
    try:
        stash_args = []
        if include_untracked:
            stash_args.append("-u")
        if message:
            stash_args.extend(["-m", message])
        repo.git.stash("push", *stash_args)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to stash changes: {e}")

def stash_pop(repo: Repo, stash_ref: str = "stash@{0}") -> None:
    """
    Apply and remove the most recent stash.
    
    :param repo: The Repo object to pop stash from.
    :param stash_ref: Reference to specific stash entry.
    """
    try:
        repo.git.stash("pop", stash_ref)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to pop stash: {e}")

def list_stashes(repo: Repo) -> List[str]:
    """
    List all stashes in the repository.
    
    :param repo: The Repo object to list stashes from.
    :return: List of stash entries.
    """
    try:
        stash_list = repo.git.stash("list").splitlines()
        return stash_list
    except GitCommandError as e:
        raise RuntimeError(f"Failed to list stashes: {e}")

def merge_branch(repo: Repo, branch_name: str, no_ff: bool = False) -> None:
    """
    Merge a branch into the current branch.
    
    :param repo: The Repo object to perform merge in.
    :param branch_name: Name of the branch to merge.
    :param no_ff: Whether to force a merge commit (no fast-forward).
    """
    try:
        if no_ff:
            repo.git.merge("--no-ff", branch_name)
        else:
            repo.git.merge(branch_name)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to merge branch '{branch_name}': {e}")

def rebase_branch(repo: Repo, branch_name: str, interactive: bool = False) -> None:
    """
    Rebase current branch onto another branch.
    
    :param repo: The Repo object to perform rebase in.
    :param branch_name: Name of the branch to rebase onto.
    :param interactive: Whether to perform interactive rebase.
    """
    try:
        if interactive:
            repo.git.rebase("-i", branch_name)
        else:
            repo.git.rebase(branch_name)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to rebase onto '{branch_name}': {e}")

def cherry_pick(repo: Repo, commit_ref: str) -> None:
    """
    Cherry-pick a specific commit onto the current branch.
    
    :param repo: The Repo object to perform cherry-pick in.
    :param commit_ref: Reference to the commit to cherry-pick.
    """
    try:
        repo.git.cherry_pick(commit_ref)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to cherry-pick commit '{commit_ref}': {e}")

def init_repo(path: str, bare: bool = False) -> Repo:
    """
    Initialize a new Git repository.
    
    :param path: Path where to initialize the repository.
    :param bare: Whether to create a bare repository.
    :return: The initialized Repo object.
    """
    try:
        return Repo.init(path, bare=bare)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to initialize repository at '{path}': {e}")

def get_untracked_files(repo: Repo) -> List[str]:
    """
    Get list of untracked files in the repository.
    
    :param repo: The Repo object to check for untracked files.
    :return: List of untracked file paths.
    """
    try:
        return repo.untracked_files
    except GitCommandError as e:
        raise RuntimeError(f"Failed to get untracked files: {e}")

def add_files(repo: Repo, files: List[str]) -> None:
    """
    Add files to the staging area.
    
    :param repo: The Repo object to add files to.
    :param files: List of file paths to add.
    """
    try:
        repo.index.add(files)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to add files to staging area: {e}")

def remove_files(repo: Repo, files: List[str], cached: bool = False) -> None:
    """
    Remove files from the repository or staging area.
    
    :param repo: The Repo object to remove files from.
    :param files: List of file paths to remove.
    :param cached: Whether to only remove from staging area (keep in working dir).
    """
    try:
        if cached:
            repo.index.remove(files, working_tree=False)
        else:
            repo.index.remove(files, working_tree=True)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to remove files: {e}")

def get_file_content(repo: Repo, file_path: str, commit_ref: str = "HEAD") -> str:
    """
    Get the content of a file at a specific commit.
    
    :param repo: The Repo object to get file content from.
    :param file_path: Path to the file.
    :param commit_ref: Reference to the commit.
    :return: File content as string.
    """
    try:
        commit = repo.commit(commit_ref)
        blob = commit.tree[file_path]
        return blob.data_stream.read().decode('utf-8')
    except GitCommandError as e:
        raise RuntimeError(f"Failed to get file content for '{file_path}': {e}")

def blame_file(repo: Repo, file_path: str) -> List[str]:
    """
    Get blame information for a file.
    
    :param repo: The Repo object to get blame from.
    :param file_path: Path to the file to blame.
    :return: List of blame lines.
    """
    try:
        blame_output = repo.git.blame(file_path).splitlines()
        return blame_output
    except GitCommandError as e:
        raise RuntimeError(f"Failed to get blame for '{file_path}': {e}")
