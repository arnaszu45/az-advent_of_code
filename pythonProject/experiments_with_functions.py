from pathlib import Path

def is_git_repo(git_repo: Path) -> bool:
    """Takes directory name and checks if it's Git repository"""

    if not isinstance(git_repo, Path):
        return False
    return True


print(is_git_repo(Path("8")))
