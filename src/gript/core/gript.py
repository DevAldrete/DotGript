"""
Gript Git Module
This module provides comprehensive functionality to interact with Git repositories.
This includes cloning repositories, checking the status of the working directory,
committing changes, managing branches, handling remotes, working with tags,
and various other Git operations with advanced features and improved error handling.
This module is designed to be used with the Gript framework and is intended to be used
as a comprehensive replacement for essential Git functionality.

Enhanced with DotGript automation integration for .gript folder and config management.
"""
import os
import json
from pathlib import Path
from datetime import datetime
from git import Repo, GitCommandError
from typing import Optional, List, Dict, Union, Any

class GitError(Exception):
    """Enhanced Git error with detailed message and solution suggestions."""
    
    def __init__(self, operation: str, original_error: str, suggestions: Optional[List[str]] = None):
        self.operation = operation
        self.original_error = original_error
        self.suggestions = suggestions or []
        
        message = f"Git operation '{operation}' failed: {original_error}"
        if self.suggestions:
            message += "\n\nPossible solutions:"
            for i, suggestion in enumerate(self.suggestions, 1):
                message += f"\n  {i}. {suggestion}"
        
        super().__init__(message)

def _handle_git_error(operation: str, error: GitCommandError) -> GitError:
    """Convert GitCommandError to more informative GitError with suggestions."""
    error_msg = str(error)
    suggestions = []
    
    # Repository not found or invalid
    if "not a git repository" in error_msg.lower():
        suggestions = [
            "Initialize a Git repository with 'gript git init'",
            "Navigate to a directory that contains a Git repository",
            "Clone an existing repository with 'gript git clone <url>'"
        ]
    
    # Branch related errors
    elif "branch" in error_msg.lower() and "does not exist" in error_msg.lower():
        suggestions = [
            "Check existing branches with 'gript git branches'",
            "Create the branch first with 'gript git create-branch <name>'",
            "Fetch remote branches with 'gript git fetch'"
        ]
    
    # Remote related errors
    elif "remote" in error_msg.lower():
        if "does not exist" in error_msg.lower():
            suggestions = [
                "Check existing remotes with 'gript git remotes'",
                "Add the remote with 'gript git add-remote <name> <url>'",
                "Verify the remote name is correct"
            ]
        elif "permission denied" in error_msg.lower() or "authentication" in error_msg.lower():
            suggestions = [
                "Check your SSH keys or credentials",
                "Verify you have access to the repository",
                "Use HTTPS URL if SSH is not configured",
                "Contact the repository administrator for access"
            ]
    
    # Merge conflicts
    elif "conflict" in error_msg.lower() or "merge" in error_msg.lower():
        suggestions = [
            "Resolve conflicts manually in affected files",
            "Use 'gript git status' to see conflicted files",
            "After resolving, use 'gript git add' and 'gript git commit'",
            "Use 'gript git merge --abort' to cancel the merge"
        ]
    
    # Staging/commit issues
    elif "nothing to commit" in error_msg.lower():
        suggestions = [
            "Add files to staging with 'gript git add <files>'",
            "Check repository status with 'gript git status'",
            "Create or modify files before committing"
        ]
    
    # Push/pull issues
    elif "push" in operation.lower() and ("rejected" in error_msg.lower() or "non-fast-forward" in error_msg.lower()):
        suggestions = [
            "Pull latest changes first with 'gript git pull'",
            "Resolve any merge conflicts if they occur",
            "Use force push with caution: add --force flag (be careful!)"
        ]
    
    # Default suggestions
    if not suggestions:
        suggestions = [
            "Check repository status with 'gript git status'",
            "Verify you're in the correct directory",
            "Ensure you have necessary permissions",
            "Check Git configuration with 'git config --list'"
        ]
    
    return GitError(operation, error_msg, suggestions)


class GriptGit:
    """
    Enhanced Git operations class that integrates with DotGript automation system.
    This class wraps basic Git operations with automation features like configuration
    management, branch metadata tracking, and .gript folder integration.
    """
    
    def __init__(self, repo_path: str = ".", config: Optional[Any] = None):
        """
        Initialize GriptGit with repository path and optional configuration.
        
        :param repo_path: Path to the Git repository
        :param config: Optional automation configuration
        """
        # Import here to avoid circular imports
        from .gript_automations import GitAutomationSuite
        
        self.repo_path = repo_path
        try:
            self.repo = Repo(repo_path)
        except Exception:
            raise GitError("initialize repository", f"Invalid Git repository: {repo_path}")
        
        # Initialize automation suite for enhanced features
        self.automation = GitAutomationSuite(repo_path, config)
        self._gript_dir = Path(self.repo.working_dir) / ".gript"
        self._ensure_gript_dir()
    
    def _ensure_gript_dir(self):
        """Ensure .gript directory exists and is properly configured"""
        self._gript_dir.mkdir(exist_ok=True)
        
        # Create metadata directory for branch tracking
        (self._gript_dir / "branches").mkdir(exist_ok=True)
        (self._gript_dir / "commits").mkdir(exist_ok=True)
        (self._gript_dir / "logs").mkdir(exist_ok=True)
    
    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """Log Git operations to .gript/logs for audit trail"""
        log_file = self._gript_dir / "logs" / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
            "user": os.getenv("USER", "unknown"),
            "branch": self.get_current_branch()
        }
        
        # Append to daily log file
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _update_operation_stats(self, operation: str):
        """Update operation statistics in .gript folder"""
        stats_file = self._gript_dir / "stats.json"
        stats = {}
        
        if stats_file.exists():
            with open(stats_file, "r") as f:
                stats = json.load(f)
        
        # Update operation count
        if operation not in stats:
            stats[operation] = 0
        stats[operation] += 1
        stats["last_operation"] = datetime.now().isoformat()
        
        # Save updated stats
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
    
    # Enhanced Git operations with automation integration
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None, 
                      amend: bool = False, allow_empty: bool = False,
                      use_conventional_commits: bool = True) -> str:
        """
        Enhanced commit with automation features and .gript integration.
        
        :param message: Commit message
        :param files: Optional list of files to commit
        :param amend: Whether to amend the last commit
        :param allow_empty: Whether to allow empty commits
        :param use_conventional_commits: Whether to use conventional commit validation
        :return: The commit hash
        """
        try:
            # Use automation suite for smart commit if enabled
            if use_conventional_commits and hasattr(self.automation, 'smart_commit'):
                result = self.automation.smart_commit(
                    message=message,
                    files=files,
                    auto_stage=True
                )
                if result.get('success'):
                    commit_hash = result.get('commit_hash', '')
                    self._log_operation("commit", {
                        "message": message,
                        "files": files or [],
                        "hash": commit_hash,
                        "conventional": True
                    })
                    self._update_operation_stats("commit")
                    return commit_hash
                else:
                    raise GitError("commit changes", result.get('error', 'Unknown error'))
            
            # Fallback to basic commit
            return commit_changes(self.repo, message, files, amend, allow_empty)
            
        except Exception as e:
            raise _handle_git_error("commit changes", e)
    
    def create_branch(self, branch_name: str, issue_number: Optional[int] = None,
                     from_branch: Optional[str] = None, interactive: bool = False) -> Dict[str, Any]:
        """
        Enhanced branch creation with automation features.
        
        :param branch_name: Name of the new branch
        :param issue_number: Optional issue number for tracking
        :param from_branch: Base branch to create from
        :param interactive: Whether to use interactive naming
        :return: Dictionary with branch creation results
        """
        try:
            # Use automation suite for smart feature start
            if hasattr(self.automation, 'smart_feature_start'):
                result = self.automation.smart_feature_start(
                    feature_name=branch_name,
                    issue_number=issue_number,
                    from_branch=from_branch,
                    interactive=interactive
                )
                
                self._log_operation("create_branch", {
                    "branch_name": result.get('branch_name', branch_name),
                    "base_branch": result.get('base_branch'),
                    "issue_number": issue_number,
                    "automated": True
                })
                self._update_operation_stats("create_branch")
                return result
            
            # Fallback to basic branch creation
            create_branch(self.repo, branch_name)
            return {"success": True, "branch_name": branch_name}
            
        except Exception as e:
            raise _handle_git_error("create branch", e)
    
    def push_changes(self, remote_name: str = 'origin', branch_name: Optional[str] = None,
                    force: bool = False, set_upstream: bool = False) -> str:
        """
        Enhanced push with automation features and logging.
        
        :param remote_name: Name of the remote repository
        :param branch_name: Name of the branch to push
        :param force: Whether to force push
        :param set_upstream: Whether to set up tracking
        :return: Push result information
        """
        try:
            current_branch = branch_name or self.get_current_branch()
            result = push_changes(self.repo, remote_name, current_branch, force, set_upstream)
            
            self._log_operation("push", {
                "remote": remote_name,
                "branch": current_branch,
                "force": force,
                "set_upstream": set_upstream
            })
            self._update_operation_stats("push")
            return result
            
        except Exception as e:
            raise _handle_git_error("push changes", e)
    
    def pull_changes(self, remote_name: str = 'origin', branch_name: Optional[str] = None,
                    rebase: bool = False) -> str:
        """
        Enhanced pull with automation features and logging.
        
        :param remote_name: Name of the remote repository
        :param branch_name: Name of the branch to pull from
        :param rebase: Whether to rebase instead of merge
        :return: Pull result information
        """
        try:
            current_branch = branch_name or self.get_current_branch()
            result = pull_changes(self.repo, remote_name, current_branch, rebase)
            
            self._log_operation("pull", {
                "remote": remote_name,
                "branch": current_branch,
                "rebase": rebase
            })
            self._update_operation_stats("pull")
            return result
            
        except Exception as e:
            raise _handle_git_error("pull changes", e)
    
    def get_current_branch(self) -> str:
        """Get the name of the current branch"""
        return get_current_branch(self.repo)
    
    def get_repo_status(self) -> Dict[str, List[str]]:
        """Get enhanced repository status with automation context"""
        status = get_repo_status(self.repo)
        
        # Add automation context if available
        if hasattr(self.automation, 'list_active_features'):
            try:
                status['active_features'] = [f['name'] for f in self.automation.list_active_features()]
            except Exception:
                status['active_features'] = []
        
        self._update_operation_stats("status")
        return status
    
    def get_gript_info(self) -> Dict[str, Any]:
        """Get information about .gript configuration and stats"""
        info = {
            "gript_dir": str(self._gript_dir),
            "config_exists": (self._gript_dir / ".conf.json").exists(),
            "stats": {},
            "recent_operations": []
        }
        
        # Load stats if available
        stats_file = self._gript_dir / "stats.json"
        if stats_file.exists():
            with open(stats_file, "r") as f:
                info["stats"] = json.load(f)
        
        # Load recent operations from today's log
        today_log = self._gript_dir / "logs" / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        if today_log.exists():
            with open(today_log, "r") as f:
                lines = f.readlines()
                info["recent_operations"] = [json.loads(line.strip()) for line in lines[-10:]]
        
        return info


def clone_repo(repo_url: str, dest_dir: str, setup_gript: bool = True) -> Repo:
    """
    Clone a Git repository from the given URL to the specified destination directory.
    Enhanced with automatic .gript setup.
    
    :param repo_url: URL of the repository to clone.
    :param dest_dir: Directory where the repository will be cloned.
    :param setup_gript: Whether to automatically setup .gript folder
    :return: The cloned Repo object.
    """
    try:
        repo = Repo.clone_from(repo_url, dest_dir)
        
        # Setup .gript folder if requested
        if setup_gript:
            gript_git = GriptGit(dest_dir)
            gript_git._log_operation("clone", {
                "repo_url": repo_url,
                "dest_dir": dest_dir,
                "setup_gript": setup_gript
            })
        
        return repo
    except GitCommandError as e:
        raise _handle_git_error("clone repository", e)
    
def get_repo_status(repo: Repo) -> Dict[str, List[str]]:
    """
    Get the status of the working directory of the given repository.
    
    :param repo: The Repo object to check.
    :return: A dictionary with categorized file statuses.
    """
    try:
        # Get different types of file changes
        status = {
            'staged': [],
            'modified': [],
            'untracked': repo.untracked_files,
            'deleted': [],
            'renamed': [],
            'conflicts': []
        }
        
        # Check staged files
        staged_files = repo.index.diff("HEAD")
        for diff in staged_files:
            if diff.change_type == 'A':
                status['staged'].append(f"new file:   {diff.b_path}")
            elif diff.change_type == 'M':
                status['staged'].append(f"modified:   {diff.b_path}")
            elif diff.change_type == 'D':
                status['staged'].append(f"deleted:    {diff.a_path}")
            elif diff.change_type == 'R':
                status['renamed'].append(f"renamed:    {diff.a_path} -> {diff.b_path}")
        
        # Check unstaged files
        unstaged_files = repo.index.diff(None)
        for diff in unstaged_files:
            if diff.change_type == 'M':
                status['modified'].append(diff.a_path)
            elif diff.change_type == 'D':
                status['deleted'].append(diff.a_path)
        
        return status
        
    except GitCommandError as e:
        raise _handle_git_error("get repository status", e)

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
        elif not amend:
            # Only add all changes if not amending and no specific files given
            repo.git.add(A=True)
        
        commit_args = []
        if amend:
            commit_args.append("--amend")
        if allow_empty:
            commit_args.append("--allow-empty")
        
        if amend and not message:
            # If amending without new message, reuse the previous one
            commit_args.append("--no-edit")
            repo.git.commit(*commit_args)
        else:
            repo.index.commit(message, **{
                'amend': amend,
                'allow_empty': allow_empty
            } if amend or allow_empty else {})
        
        # Return the commit hash
        return repo.head.commit.hexsha
        
    except GitCommandError as e:
        raise _handle_git_error("commit changes", e)

def push_changes(repo: Repo, remote_name: str = 'origin', branch_name: str = 'main', 
                force: bool = False, set_upstream: bool = False) -> str:
    """
    Push committed changes to the specified remote repository and branch.
    
    :param repo: The Repo object to push changes from.
    :param remote_name: Name of the remote repository (default is 'origin').
    :param branch_name: Name of the branch to push to (default is 'main').
    :param force: Whether to force push (use with caution).
    :param set_upstream: Whether to set up tracking relationship.
    :return: Push result information.
    """
    try:
        push_args = []
        if force:
            push_args.append("--force")
        if set_upstream:
            push_args.append("--set-upstream")
        
        remote = repo.remotes[remote_name]
        if set_upstream:
            result = remote.push(f"{branch_name}:{branch_name}", *push_args)
        else:
            result = remote.push(branch_name, *push_args)
        
        # Extract useful information from push result
        if result:
            push_info = result[0]
            if push_info.flags & push_info.UP_TO_DATE:
                return f"Branch {branch_name} is up to date"
            elif push_info.flags & push_info.FAST_FORWARD:
                return f"Successfully pushed {branch_name} (fast-forward)"
            elif push_info.flags & push_info.FORCED_UPDATE:
                return f"Force pushed {branch_name} (forced update)"
            else:
                return f"Successfully pushed {branch_name}"
        
        return f"Successfully pushed {branch_name}"
        
    except GitCommandError as e:
        raise _handle_git_error("push changes", e)
    except KeyError:
        raise GitError("push changes", f"Remote '{remote_name}' not found", [
            f"Add the remote with 'gript git add-remote {remote_name} <url>'",
            "Check existing remotes with 'gript git remotes'",
            "Verify the remote name is correct"
        ])
    
def pull_changes(repo: Repo, remote_name: str = 'origin', branch_name: str = 'main',
                rebase: bool = False) -> str:
    """
    Pull changes from the specified remote repository and branch.
    
    :param repo: The Repo object to pull changes into.
    :param remote_name: Name of the remote repository (default is 'origin').
    :param branch_name: Name of the branch to pull from (default is 'main').
    :param rebase: Whether to rebase instead of merge when pulling.
    :return: Pull result information.
    """
    try:
        remote = repo.remotes[remote_name]
        
        if rebase:
            result = remote.pull(branch_name, rebase=True)
        else:
            result = remote.pull(branch_name)
        
        if result:
            pull_info = result[0]
            if pull_info.flags & pull_info.HEAD_UPTODATE:
                return f"Already up to date with {remote_name}/{branch_name}"
            elif pull_info.flags & pull_info.FAST_FORWARD:
                return f"Successfully pulled from {remote_name}/{branch_name} (fast-forward)"
            else:
                return f"Successfully pulled from {remote_name}/{branch_name}"
        
        return f"Successfully pulled from {remote_name}/{branch_name}"
        
    except GitCommandError as e:
        raise _handle_git_error("pull changes", e)
    except KeyError:
        raise GitError("pull changes", f"Remote '{remote_name}' not found", [
            f"Add the remote with 'gript git add-remote {remote_name} <url>'",
            "Check existing remotes with 'gript git remotes'",
            "Verify the remote name is correct"
        ])

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
        # Build arguments for iter_commits
        kwargs = {'max_count': max_count}
        if since:
            kwargs['since'] = since
        if until:
            kwargs['until'] = until
        if author:
            kwargs['author'] = author
        if grep:
            kwargs['grep'] = grep
        
        commits = list(repo.iter_commits(**kwargs))
        log_entries = []
        
        for commit in commits:
            # Calculate relative time
            commit_time = commit.committed_datetime
            now = commit_time.now(commit_time.tzinfo)
            time_diff = now - commit_time
            
            if time_diff.days > 0:
                relative_time = f"{time_diff.days} days ago"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                relative_time = f"{hours} hours ago"
            elif time_diff.seconds > 60:
                minutes = time_diff.seconds // 60
                relative_time = f"{minutes} minutes ago"
            else:
                relative_time = "just now"
            
            if oneline:
                entry = {
                    'hash': commit.hexsha[:7],
                    'message': commit.summary,
                    'author': commit.author.name,
                    'date': relative_time,
                    'format': 'oneline'
                }
            else:
                # Get file stats
                stats = commit.stats.total
                files_changed = stats.get('files', 0)
                insertions = stats.get('insertions', 0)
                deletions = stats.get('deletions', 0)
                
                entry = {
                    'hash': commit.hexsha,
                    'short_hash': commit.hexsha[:7],
                    'author_name': commit.author.name,
                    'author_email': commit.author.email,
                    'date': commit_time.strftime('%a %b %d %H:%M:%S %Y %z'),
                    'relative_date': relative_time,
                    'message': commit.message.strip(),
                    'summary': commit.summary,
                    'files_changed': files_changed,
                    'insertions': insertions,
                    'deletions': deletions,
                    'format': 'detailed'
                }
            
            log_entries.append(entry)
        
        return log_entries
        
    except GitCommandError as e:
        raise _handle_git_error("get git log", e)

def show_commit(repo: Repo, commit_ref: str = "HEAD", show_stats: bool = True) -> Dict[str, str]:
    """
    Show detailed information about a specific commit.
    
    :param repo: The Repo object to get commit info from.
    :param commit_ref: Reference to the commit (hash, HEAD, etc.).
    :param show_stats: Whether to include file change statistics.
    :return: Dictionary with detailed commit information.
    """
    try:
        commit = repo.commit(commit_ref)
        
        # Get commit stats
        stats = commit.stats.total
        files_changed = stats.get('files', 0)
        insertions = stats.get('insertions', 0)
        deletions = stats.get('deletions', 0)
        
        # Build the commit info
        info = {
            'hash': commit.hexsha,
            'short_hash': commit.hexsha[:7],
            'author_name': commit.author.name,
            'author_email': commit.author.email,
            'committer_name': commit.committer.name,
            'committer_email': commit.committer.email,
            'author_date': commit.authored_datetime.strftime('%a %b %d %H:%M:%S %Y %z'),
            'commit_date': commit.committed_datetime.strftime('%a %b %d %H:%M:%S %Y %z'),
            'message': commit.message.strip(),
            'summary': commit.summary,
            'files_changed': files_changed,
            'insertions': insertions,
            'deletions': deletions,
            'parents': [parent.hexsha[:7] for parent in commit.parents],
            'diff': ''
        }
        
        # Get diff if there are parents
        if commit.parents and show_stats:
            diffs = commit.diff(commit.parents[0])
            diff_text = ""
            for diff in diffs:
                if diff.a_path:
                    diff_text += f"diff --git a/{diff.a_path} b/{diff.b_path or diff.a_path}\n"
                    diff_text += f"--- a/{diff.a_path}\n"
                    diff_text += f"+++ b/{diff.b_path or diff.a_path}\n"
                    if diff.diff:
                        diff_text += diff.diff.decode('utf-8', errors='ignore')
                    diff_text += "\n"
            info['diff'] = diff_text
        
        return info
        
    except GitCommandError as e:
        raise _handle_git_error(f"show commit '{commit_ref}'", e)

def get_diff(repo: Repo, 
            cached: bool = False, 
            commit1: Optional[str] = None, 
            commit2: Optional[str] = None,
            file_path: Optional[str] = None,
            context_lines: int = 3,
            word_diff: bool = False) -> Dict[str, Union[str, List[Dict]]]:
    """
    Get differences between commits, staging area, or working directory.
    
    :param repo: The Repo object to get differences from.
    :param cached: Show differences between staging area and last commit.
    :param commit1: First commit to compare (if None, uses HEAD).
    :param commit2: Second commit to compare (if None, uses working dir).
    :param file_path: Specific file to show diff for.
    :param context_lines: Number of context lines to show.
    :param word_diff: Show word-level differences.
    :return: Dictionary with diff information and file changes.
    """
    try:
        diff_data = {
            'summary': '',
            'stats': {},
            'files': [],
            'diff_text': ''
        }
        
        # Determine what to diff
        if cached:
            # Staged changes vs HEAD
            diffs = repo.head.commit.diff(cached=True, create_patch=True)
            diff_data['summary'] = "Changes to be committed (staged)"
        elif commit1 and commit2:
            # Between two commits
            commit1_obj = repo.commit(commit1)
            commit2_obj = repo.commit(commit2)
            diffs = commit1_obj.diff(commit2_obj, create_patch=True)
            diff_data['summary'] = f"Differences between {commit1[:7]} and {commit2[:7]}"
        elif commit1:
            # Commit vs working directory
            commit1_obj = repo.commit(commit1)
            diffs = commit1_obj.diff(None, create_patch=True)
            diff_data['summary'] = f"Changes since {commit1[:7]}"
        else:
            # Working directory vs HEAD
            diffs = repo.head.commit.diff(None, create_patch=True)
            diff_data['summary'] = "Changes not staged for commit"
        
        # Filter by specific file if requested
        if file_path:
            diffs = [d for d in diffs if d.a_path == file_path or d.b_path == file_path]
            diff_data['summary'] += f" (file: {file_path})"
        
        # Process diffs
        total_insertions = 0
        total_deletions = 0
        diff_text = ""
        
        for diff in diffs:
            file_info = {
                'path': diff.b_path or diff.a_path,
                'change_type': diff.change_type,
                'insertions': 0,
                'deletions': 0,
                'is_binary': False
            }
            
            # Check if binary file
            if diff.a_blob and diff.a_blob.size > 0:
                try:
                    diff.a_blob.data_stream.read(1024).decode('utf-8')
                except UnicodeDecodeError:
                    file_info['is_binary'] = True
            
            if not file_info['is_binary'] and diff.diff:
                patch_text = diff.diff.decode('utf-8', errors='ignore')
                
                # Count insertions and deletions
                for line in patch_text.split('\n'):
                    if line.startswith('+') and not line.startswith('+++'):
                        file_info['insertions'] += 1
                        total_insertions += 1
                    elif line.startswith('-') and not line.startswith('---'):
                        file_info['deletions'] += 1
                        total_deletions += 1
                
                # Add to diff text
                diff_text += f"diff --git a/{diff.a_path or 'dev/null'} b/{diff.b_path or 'dev/null'}\n"
                if diff.new_file:
                    diff_text += f"new file mode {oct(diff.b_blob.mode)[-3:]}\n"
                elif diff.deleted_file:
                    diff_text += "deleted file mode 100644\n"
                
                diff_text += patch_text + "\n"
            
            diff_data['files'].append(file_info)
        
        diff_data['stats'] = {
            'files_changed': len(diffs),
            'insertions': total_insertions,
            'deletions': total_deletions
        }
        diff_data['diff_text'] = diff_text
        
        return diff_data
        
    except GitCommandError as e:
        raise _handle_git_error("get diff", e)

def reset_repo(repo: Repo, 
              mode: str = "mixed", 
              commit_ref: str = "HEAD",
              paths: Optional[List[str]] = None) -> Dict[str, Union[str, List[str]]]:
    """
    Reset the repository to a specific commit or reset specific files.
    
    :param repo: The Repo object to reset.
    :param mode: Reset mode ('soft', 'mixed', 'hard').
    :param commit_ref: Reference to reset to.
    :param paths: Specific files to reset (if provided, mode is ignored).
    :return: Dictionary with reset operation details.
    """
    try:
        reset_info = {
            'mode': mode,
            'commit_ref': commit_ref,
            'reset_files': [],
            'message': ''
        }
        
        if paths:
            # Reset specific files
            for path in paths:
                repo.git.checkout(commit_ref, "--", path)
                reset_info['reset_files'].append(path)
            reset_info['message'] = f"Reset {len(paths)} file(s) to {commit_ref}"
        else:
            # Reset entire repository
            if mode == "soft":
                repo.git.reset("--soft", commit_ref)
                reset_info['message'] = f"Soft reset to {commit_ref} (index and working tree unchanged)"
            elif mode == "hard":
                repo.git.reset("--hard", commit_ref)
                reset_info['message'] = f"Hard reset to {commit_ref} (index and working tree reset)"
            else:  # mixed (default)
                repo.git.reset("--mixed", commit_ref)
                reset_info['message'] = f"Mixed reset to {commit_ref} (index reset, working tree unchanged)"
        
        return reset_info
        
    except GitCommandError as e:
        if "ambiguous argument" in str(e):
            raise _handle_git_error(f"reset to '{commit_ref}'", e, [
                f"Check if commit '{commit_ref}' exists: git log --oneline -n 10",
                "Use full commit hash instead of short reference",
                "Use 'git reflog' to see recent commits if you lost track"
            ])
        else:
            raise _handle_git_error("reset repository", e)

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

def init_repo(path: str, bare: bool = False, setup_gript: bool = True) -> Repo:
    """
    Initialize a new Git repository with optional .gript setup.
    
    :param path: Path where to initialize the repository.
    :param bare: Whether to create a bare repository.
    :param setup_gript: Whether to automatically setup .gript folder
    :return: The initialized Repo object.
    """
    try:
        repo = Repo.init(path, bare=bare)
        
        # Setup .gript folder if requested and not bare
        if setup_gript and not bare:
            gript_git = GriptGit(path)
            gript_git._log_operation("init", {
                "path": path,
                "bare": bare,
                "setup_gript": setup_gript
            })
        
        return repo
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

def blame_file(repo: Repo, file_path: str) -> Dict[str, Union[str, List[Dict]]]:
    """
    Get blame information for a file with detailed commit info.
    
    :param repo: The Repo object to get blame from.
    :param file_path: Path to the file to blame.
    :return: Dictionary with blame information.
    """
    try:
        blame_info = {
            'file_path': file_path,
            'lines': []
        }
        
        # Get blame with porcelain format for better parsing
        blame_output = repo.git.blame('--porcelain', file_path)
        
        lines = blame_output.split('\n')
        current_commit = {}
        line_number = 1
        
        for line in lines:
            if line and not line.startswith('\t'):
                if len(line.split()) >= 4 and line.split()[0].isalnum():
                    # New commit line
                    parts = line.split()
                    commit_hash = parts[0]
                    if commit_hash not in [item.get('commit_hash') for item in blame_info['lines']]:
                        try:
                            commit = repo.commit(commit_hash)
                            current_commit = {
                                'commit_hash': commit_hash,
                                'short_hash': commit_hash[:7],
                                'author': commit.author.name,
                                'author_email': commit.author.email,
                                'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                                'summary': commit.summary
                            }
                        except Exception:
                            current_commit = {
                                'commit_hash': commit_hash,
                                'short_hash': commit_hash[:7],
                                'author': 'Unknown',
                                'author_email': '',
                                'date': 'Unknown',
                                'summary': 'Unknown'
                            }
            elif line.startswith('\t'):
                # Content line
                content = line[1:]  # Remove tab
                blame_info['lines'].append({
                    'line_number': line_number,
                    'content': content,
                    **current_commit
                })
                line_number += 1
        
        return blame_info
        
    except GitCommandError as e:
        raise _handle_git_error(f"blame file '{file_path}'", e)


def cherry_pick_commits(repo: Repo, 
                       commit_refs: List[str], 
                       no_commit: bool = False,
                       mainline: Optional[int] = None) -> Dict[str, Union[str, List[str]]]:
    """
    Cherry-pick one or more commits.
    
    :param repo: The Repo object to cherry-pick in.
    :param commit_refs: List of commit references to cherry-pick.
    :param no_commit: Don't automatically commit after cherry-pick.
    :param mainline: Parent number for merge commits (1-based).
    :return: Dictionary with cherry-pick results.
    """
    try:
        picked_commits = []
        conflicts = []
        
        for commit_ref in commit_refs:
            try:
                args = ['cherry-pick']
                if no_commit:
                    args.append('--no-commit')
                if mainline:
                    args.extend(['-m', str(mainline)])
                args.append(commit_ref)
                
                repo.git.execute(args)
                picked_commits.append(commit_ref)
                
            except GitCommandError as e:
                if 'conflict' in str(e).lower():
                    conflicts.append({
                        'commit': commit_ref,
                        'error': str(e)
                    })
                else:
                    raise e
        
        return {
            'picked_commits': picked_commits,
            'conflicts': conflicts,
            'message': f"Cherry-picked {len(picked_commits)} commit(s)"
        }
        
    except GitCommandError as e:
        raise _handle_git_error(f"cherry-pick commits {commit_refs}", e, [
            "Resolve conflicts and run 'git cherry-pick --continue'",
            "Use 'git cherry-pick --abort' to cancel the operation",
            "For merge commits, use --mainline option to specify parent"
        ])


def rebase_interactive(repo: Repo, 
                      base_commit: str,
                      continue_rebase: bool = False,
                      abort_rebase: bool = False,
                      skip_commit: bool = False) -> Dict[str, str]:
    """
    Perform interactive rebase operations.
    
    :param repo: The Repo object to rebase.
    :param base_commit: Base commit to rebase onto.
    :param continue_rebase: Continue an in-progress rebase.
    :param abort_rebase: Abort the current rebase.
    :param skip_commit: Skip the current commit during rebase.
    :return: Dictionary with rebase status.
    """
    try:
        result = {'operation': '', 'message': ''}
        
        if abort_rebase:
            repo.git.rebase('--abort')
            result['operation'] = 'abort'
            result['message'] = 'Rebase aborted successfully'
        elif continue_rebase:
            repo.git.rebase('--continue')
            result['operation'] = 'continue'
            result['message'] = 'Rebase continued'
        elif skip_commit:
            repo.git.rebase('--skip')
            result['operation'] = 'skip'
            result['message'] = 'Current commit skipped, rebase continued'
        else:
            repo.git.rebase('-i', base_commit)
            result['operation'] = 'start'
            result['message'] = f'Interactive rebase started onto {base_commit}'
        
        return result
        
    except GitCommandError as e:
        if 'conflict' in str(e).lower():
            raise _handle_git_error(f"rebase onto {base_commit}", e, [
                "Resolve conflicts in the affected files",
                "Stage resolved files with 'git add <file>'",
                "Continue rebase with 'git rebase --continue'",
                "Or abort rebase with 'git rebase --abort'"
            ])
        else:
            raise _handle_git_error(f"rebase onto {base_commit}", e)


# Factory and utility functions for enhanced Git operations

def create_gript_git(repo_path: str = ".", config: Optional[Any] = None) -> GriptGit:
    """
    Factory function to create a GriptGit instance with automation features.
    
    :param repo_path: Path to the Git repository
    :param config: Optional automation configuration
    :return: GriptGit instance
    """
    return GriptGit(repo_path, config)


def setup_gript_automation(repo_path: str = ".", 
                          workflow_type: str = "github_flow",
                          enforce_conventional_commits: bool = True,
                          auto_squash_merge: bool = True) -> GriptGit:
    """
    Setup a repository with DotGript automation features.
    
    :param repo_path: Path to the Git repository
    :param workflow_type: Type of workflow (github_flow, gitflow, etc.)
    :param enforce_conventional_commits: Whether to enforce conventional commits
    :param auto_squash_merge: Whether to enable auto squash merge
    :return: Configured GriptGit instance
    """
    from .gript_automations import AutomationConfig, WorkflowType
    
    # Map string workflow type to enum
    workflow_map = {
        "github_flow": WorkflowType.GITHUB_FLOW,
        "gitflow": WorkflowType.GITFLOW,
        "gitlab_flow": WorkflowType.GITLAB_FLOW,
        "custom": WorkflowType.CUSTOM
    }
    
    config = AutomationConfig(
        workflow_type=workflow_map.get(workflow_type, WorkflowType.GITHUB_FLOW),
        enforce_conventional_commits=enforce_conventional_commits,
        auto_squash_merge=auto_squash_merge
    )
    
    return GriptGit(repo_path, config)


def get_gript_status(repo_path: str = ".") -> Dict[str, Any]:
    """
    Get comprehensive status including .gript automation info.
    
    :param repo_path: Path to the Git repository
    :return: Dictionary with comprehensive status
    """
    gript_git = GriptGit(repo_path)
    
    return {
        "git_status": gript_git.get_repo_status(),
        "gript_info": gript_git.get_gript_info(),
        "current_branch": gript_git.get_current_branch(),
        "automation_enabled": hasattr(gript_git.automation, 'config')
    }


def migrate_to_gript(repo_path: str = ".") -> Dict[str, Any]:
    """
    Migrate an existing Git repository to use DotGript automation.
    
    :param repo_path: Path to the Git repository
    :return: Migration results
    """
    try:
        # Create GriptGit instance (this will setup .gript folder)
        gript_git = GriptGit(repo_path)
        
        # Log the migration
        gript_git._log_operation("migrate_to_gript", {
            "repo_path": repo_path,
            "migration_date": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": f"Successfully migrated repository at {repo_path} to DotGript",
            "gript_dir": str(gript_git._gript_dir),
            "features_enabled": [
                "operation_logging",
                "statistics_tracking", 
                "branch_metadata",
                "automation_integration"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to migrate repository at {repo_path}"
        }
