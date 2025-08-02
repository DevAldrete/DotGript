"""
Gript Git Remote Module
This module provides functions for interacting with remote repositories.
"""
from typing import List, Optional
from git import Repo, GitCommandError
from .errors import _handle_git_error

def push_changes(repo: Repo, remote_name: str = 'origin', branch_name: Optional[str] = None, 
                force: bool = False, set_upstream: bool = False) -> str:
    """
    Push committed changes to the specified remote repository and branch.
    
    :param repo: The Repo object to push changes from.
    :param remote_name: Name of the remote repository (default is 'origin').
    :param branch_name: Name of the branch to push to. If None, current branch is used.
    :param force: Whether to force push (use with caution).
    :param set_upstream: Whether to set up tracking relationship.
    :return: Push result information.
    """
    try:
        remote = repo.remote(name=remote_name)
        branch = branch_name or repo.active_branch.name
        push_info = remote.push(refspec=f"{branch}:{branch}", force=force, set_upstream=set_upstream)
        return str(push_info[0].summary)
    except GitCommandError as e:
        raise _handle_git_error("push_changes", e)
    except KeyError:
        raise _handle_git_error("push_changes", GitCommandError("push_changes", f"Remote '{remote_name}' not found."))

def pull_changes(repo: Repo, remote_name: str = 'origin', branch_name: Optional[str] = None,
                rebase: bool = False) -> str:
    """
    Pull changes from the specified remote repository and branch.
    
    :param repo: The Repo object to pull changes into.
    :param remote_name: Name of the remote repository (default is 'origin').
    :param branch_name: Name of the branch to pull from. If None, current branch is used.
    :param rebase: Whether to rebase instead of merge when pulling.
    :return: Pull result information.
    """
    try:
        remote = repo.remote(name=remote_name)
        branch = branch_name or repo.active_branch.name
        pull_info = remote.pull(refspec=branch, rebase=rebase)
        return str(pull_info[0].note)
    except GitCommandError as e:
        raise _handle_git_error("pull_changes", e)
    except KeyError:
        raise _handle_git_error("pull_changes", GitCommandError("pull_changes", f"Remote '{remote_name}' not found."))

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
        repo.remote(name=remote_name).fetch()
    except GitCommandError as e:
        raise _handle_git_error("fetch_remote", e)

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
        raise _handle_git_error("add_remote", e)
