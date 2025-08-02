"""
Gript Git Branching Module
This module provides functions for managing Git branches.
"""
from typing import List
from git import Repo, GitCommandError
from .errors import _handle_git_error

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
        raise _handle_git_error("checkout_branch", e)
    
def switch_branch(repo: Repo, branch_name: str) -> None:
    """
    Switch to a specific branch in the repository.
    
    :param repo: The Repo object to switch branches in.
    :param branch_name: Name of the branch to switch to.
    """
    try:
        repo.git.switch(branch_name)
    except GitCommandError as e:
        raise _handle_git_error("switch_branch", e)
    
def create_branch(repo: Repo, branch_name: str) -> None:
    """
    Create a new branch in the repository.
    
    :param repo: The Repo object to create the branch in.
    :param branch_name: Name of the new branch to create.
    """
    try:
        repo.create_head(branch_name)
    except GitCommandError as e:
        raise _handle_git_error("create_branch", e)
    
def remove_branch(repo: Repo, branch_name: str) -> None:
    """
    Remove a branch from the repository.
    
    :param repo: The Repo object to remove the branch from.
    :param branch_name: Name of the branch to remove.
    """
    try:
        repo.delete_head(branch_name)
    except GitCommandError as e:
        raise _handle_git_error("remove_branch", e)

def get_current_branch(repo: Repo) -> str:
    """
    Get the name of the current branch in the repository.
    
    :param repo: The Repo object to get the current branch from.
    :return: Name of the current branch.
    """
    return repo.active_branch.name if repo.active_branch else "No active branch"

def merge_branch(repo: Repo, branch_name: str, no_ff: bool = False) -> None:
    """
    Merge a branch into the current branch.
    
    :param repo: The Repo object to perform merge in.
    :param branch_name: Name of the branch to merge.
    :param no_ff: Whether to force a merge commit (no fast-forward).
    """
    try:
        args = ["--no-ff"] if no_ff else []
        repo.git.merge(branch_name, *args)
    except GitCommandError as e:
        raise _handle_git_error("merge_branch", e)

def rebase_branch(repo: Repo, branch_name: str, interactive: bool = False) -> None:
    """
    Rebase current branch onto another branch.
    
    :param repo: The Repo object to perform rebase in.
    :param branch_name: Name of the branch to rebase onto.
    :param interactive: Whether to perform interactive rebase.
    """
    try:
        args = ["-i"] if interactive else []
        repo.git.rebase(branch_name, *args)
    except GitCommandError as e:
        raise _handle_git_error("rebase_branch", e)
