"""
Gript Git Tag Module
This module provides functions for managing Git tags.
"""
from typing import List, Optional
from git import Repo, GitCommandError
from .errors import _handle_git_error

def create_tag(repo: Repo, tag_name: str, commit_ref: str = "HEAD", message: Optional[str] = None) -> None:
    """
    Create a new tag pointing to a specific commit.
    
    :param repo: The Repo object to create tag in.
    :param tag_name: Name of the tag to create.
    :param commit_ref: Reference to the commit to tag.
    :param message: Optional message for annotated tag.
    """
    try:
        repo.create_tag(tag_name, ref=commit_ref, message=message)
    except GitCommandError as e:
        raise _handle_git_error("create_tag", e)

def list_tags(repo: Repo) -> List[str]:
    """
    List all tags in the repository.
    
    :param repo: The Repo object to list tags from.
    :return: List of tag names.
    """
    try:
        return [tag.name for tag in repo.tags]
    except GitCommandError as e:
        raise _handle_git_error("list_tags", e)

def delete_tag(repo: Repo, tag_name: str) -> None:
    """
    Delete a tag from the repository.
    
    :param repo: The Repo object to delete tag from.
    :param tag_name: Name of the tag to delete.
    """
    try:
        repo.delete_tag(tag_name)
    except GitCommandError as e:
        raise _handle_git_error("delete_tag", e)
