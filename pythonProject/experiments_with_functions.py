import unittest
from pathlib import Path
import subprocess
import pytest
import tempfile
import shutil
from unittest.mock import patch, Mock


def is_git_repo(git_repo: Path) -> bool:
    """Takes directory name and checks if it's Git repository"""

    if not isinstance(git_repo, Path):
        return False

    if not git_repo.is_dir():
        return False

    result = subprocess.run(["git", "-C", str(git_repo.resolve()), "rev-parse"], capture_output=True)

    if result.returncode != 0:
        return False

    return True


@pytest.fixture()
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestSubprocess(unittest.TestCase):

    @patch("subprocess.run")
    def test_is_git_repo(self, mock_run, temp_dir):
        mock_response = Mock()
        response = "empty Git repository in C:/Users/arnas.zuklija/AppData/Local/Temp/"
        mock_response.return_value = response

        mock_run.return_value = mock_response

        git_repo = is_git_repo(Path("C:/Users/arnas.zuklija/AppData/Local/Temp/tmp3myia7ox/.git/"))
        mock_run.assert_called_with("git init")
        self.assertEquals(git_repo, response)
        result = is_git_repo(Path(temp_dir))
        assert result
