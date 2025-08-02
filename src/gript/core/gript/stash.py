"""
Gript Git Stash Module
This module provides functions for stashing changes in a Git repository.
"""
from typing import List, Optional
from git import Repo, GitCommandError
from .errors import _handle_git_error

def stash_changes(repo: Repo, message: Optional[str] = None, include_untracked: bool = False) -> None:
    """
    Stash current changes in the working directory.
    
    :param repo: The Repo object to stash changes in.
    :param message: Optional message for the stash.
    :param include_untracked: Whether to include untracked files.
    """
    try:
        args = []
        if include_untracked:
            args.append("-u")
        if message:
            repo.git.stash("save", message, *args)
        else:
            repo.git.stash(*args)
    except GitCommandError as e:
        raise _handle_git_error("stash_changes", e)

def stash_pop(repo: Repo, stash_ref: str = "stash@{0}") -> None:
    """
    Apply and remove the most recent stash.
    
    :param repo: The Repo object to pop stash from.
    :param stash_ref: Reference to specific stash entry.
    """
    try:
        repo.git.stash("pop", stash_ref)
    except GitCommandError as e:
        raise _handle_git_error("stash_pop", e)

def list_stashes(repo: Repo) -> List[str]:
    """
    List all stashes in the repository.
    
    :param repo: The Repo object to list stashes from.
    :return: List of stash entries.
    """
    try:
        return repo.git.stash("list").splitlines()
    except GitCommandError as e:
        raise _handle_git_error("list_stashes", e)
