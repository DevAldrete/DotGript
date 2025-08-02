"""
Gript Git Commit Module
This module provides functions for managing Git commits.
"""
from typing import Optional, List, Dict, Union
from git import Repo, GitCommandError
from .errors import _handle_git_error

def commit_changes(repo: Repo, message: str, files: Optional[List[str]] = None, 
                  amend: bool = False, allow_empty: bool = False) -> str:
    """
    Commit changes in the repository with the given message.
    
    :param repo: The Repo object to commit changes to.
    :param message: Commit message.
    :param files: Optional list of files to commit. If None, all staged changes will be committed.
    :param amend: Whether to amend the last commit instead of creating a new one.
    :param allow_empty: Whether to allow empty commits.
    :return: The commit hash of the created/amended commit.
    """
    try:
        if files:
            repo.index.add(files)
        
        commit_kwargs = {}
        if amend:
            commit_kwargs['amend'] = True
        if allow_empty:
            commit_kwargs['allow_empty'] = True
            
        commit = repo.index.commit(message, **commit_kwargs)
        return commit.hexsha
    except GitCommandError as e:
        raise _handle_git_error("commit_changes", e)

def get_git_log(repo: Repo, max_count: int = 10, oneline: bool = False, 
               since: Optional[str] = None, until: Optional[str] = None,
               author: Optional[str] = None, grep: Optional[str] = None,
               graph: bool = False) -> List[Dict[str, str]]:
    """
    Get the Git commit log with enhanced formatting and filtering options.
    
    :param repo: The Repo object to get the log from.
    :param max_count: Maximum number of commits to retrieve.
    :param oneline: Whether to format as one line per commit.
    :param since: Show commits after this date (e.g., "2023-01-01", "1 week ago").
    :param until: Show commits before this date.
    :param author: Filter commits by author name or email.
    :param grep: Filter commits by message content.
    :param graph: Whether to show a text-based graph of branches.
    :return: List of commit information dictionaries.
    """
    try:
        log_args = [f"--max-count={max_count}"]
        if oneline:
            log_args.append("--oneline")
        if since:
            log_args.append(f"--since={since}")
        if until:
            log_args.append(f"--until={until}")
        if author:
            log_args.append(f"--author={author}")
        if grep:
            log_args.append(f"--grep={grep}")
        if graph:
            log_args.append("--graph")
            
        log_output = repo.git.log(*log_args)
        
        # For simplicity, returning raw log. Parsing can be added if needed.
        return [{"log": log_output}]
    except GitCommandError as e:
        raise _handle_git_error("get_git_log", e)

def show_commit(repo: Repo, commit_ref: str = "HEAD", show_stats: bool = True) -> Dict[str, str]:
    """
    Show detailed information about a specific commit.
    
    :param repo: The Repo object to get commit info from.
    :param commit_ref: Reference to the commit (hash, HEAD, etc.).
    :param show_stats: Whether to include file change statistics.
    :return: Dictionary with detailed commit information.
    """
    try:
        show_args = [commit_ref]
        if show_stats:
            show_args.append("--stat")
            
        commit_info = repo.git.show(*show_args)
        return {"commit_info": commit_info}
    except GitCommandError as e:
        raise _handle_git_error("show_commit", e)

def cherry_pick(repo: Repo, commit_ref: str) -> None:
    """
    Cherry-pick a specific commit onto the current branch.
    
    :param repo: The Repo object to perform cherry-pick in.
    :param commit_ref: Reference to the commit to cherry-pick.
    """
    try:
        repo.git.cherry_pick(commit_ref)
    except GitCommandError as e:
        raise _handle_git_error("cherry_pick", e)

def cherry_pick_commits(repo: Repo, 
                       commit_refs: List[str], 
                       no_commit: bool = False,
                       mainline: Optional[int] = None) -> Dict[str, Union[str, List[str]]]:
    """
    Cherry-pick a list of commits onto the current branch.
    
    :param repo: The Repo object to perform cherry-pick in.
    :param commit_refs: List of commit references to cherry-pick.
    :param no_commit: Apply changes but do not commit.
    :param mainline: Parent number (from 1) to cherry-pick from, for merge commits.
    :return: Dictionary with cherry-pick operation details.
    """
    try:
        args = []
        if no_commit:
            args.append("--no-commit")
        if mainline:
            args.append(f"--mainline {mainline}")
            
        repo.git.cherry_pick(*args, *commit_refs)
        return {"status": "success", "cherry_picked_commits": commit_refs}
    except GitCommandError as e:
        raise _handle_git_error("cherry_pick_commits", e)
