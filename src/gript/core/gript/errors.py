"""
Gript Git Error Handling
This module contains custom exception classes and error handling utilities
for Git operations within the Gript framework.
"""
from typing import Optional, List
from git import GitCommandError

class GitError(Exception):
    """Enhanced Git error with detailed message and solution suggestions."""
    
    def __init__(self, operation: str, original_error: str, suggestions: Optional[List[str]] = None):
        self.operation = operation
        self.original_error = original_error
        self.suggestions = suggestions or []
        message = f"Error during '{operation}': {original_error}"
        if self.suggestions:
            message += "\nSuggestions:\n" + "\n".join(f"- {s}" for s in self.suggestions)
        super().__init__(message)

def _handle_git_error(operation: str, error: GitCommandError) -> GitError:
    """Convert GitCommandError to more informative GitError with suggestions."""
    error_msg = str(error)
    suggestions = []
    
    # Repository not found or invalid
    if "not a git repository" in error_msg.lower():
        suggestions.append("Ensure you are in a valid Git repository.")
        suggestions.append("Initialize a new repository with 'gript init'.")
    elif "branch" in error_msg.lower() and "does not exist" in error_msg.lower():
        suggestions.append("Check if the branch name is correct.")
        suggestions.append("Use 'gript branches list' to see available branches.")
    elif "remote" in error_msg.lower():
        suggestions.append("Verify the remote name and URL are correct.")
        suggestions.append("Use 'gript remotes list' to see configured remotes.")
    elif "conflict" in error_msg.lower() or "merge" in error_msg.lower():
        suggestions.append("Resolve the merge conflicts manually.")
        suggestions.append("Use 'git status' to see conflicting files.")
    elif "nothing to commit" in error_msg.lower():
        suggestions.append("There are no changes staged for commit.")
        suggestions.append("Use 'gript add <file>' to stage changes.")
    elif "push" in operation.lower() and ("rejected" in error_msg.lower() or "non-fast-forward" in error_msg.lower()):
        suggestions.append("Your local branch is behind the remote branch.")
        suggestions.append("Pull the latest changes with 'gript pull' before pushing.")
    
    # Default suggestions
    if not suggestions:
        suggestions.append("Check your Git configuration and repository state.")
        suggestions.append("Run 'git status' for more details.")
    
    return GitError(operation, error_msg, suggestions)
