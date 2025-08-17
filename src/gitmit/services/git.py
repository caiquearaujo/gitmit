"""Git service."""

import git


class GitService:
    """GitService is a class that provides a service for Git repositories.

    Args:
        path (str): The path to the Git repository.
    """

    def __init__(self, path):
        """Initialize the GitService class.

        Args:
            path (str): The path to the Git repository.
        """
        self.repo = GitService.buildRepo(path)
        self.path = path

        if self.repo != False:
            self.git = self.repo.git

    def getRepo(self) -> git.Repo:
        """Get the Git repository.

        Returns:
            git.Repo: The Git repository.
        """
        return self.repo

    def init(self):
        """Initialize the Git repository."""
        self.repo = git.Repo.init(self.path)
        self.git = self.repo.git

    def exists(self) -> bool:
        """Check if the Git repository exists.

        Returns:
            bool: True if the Git repository exists, False otherwise.
        """
        return self.repo != False

    def getPath(self) -> str:
        """Get the path to the Git repository.

        Returns:
            str: The path to the Git repository.
        """
        if self.repo == False:
            return self.path

        return self.repo.working_dir

    def commit(self, message: str):
        """Commit the changes.

        Args:
            message (str): A commit message.
        """
        self.git.add("--all")
        self.git.commit("-m", message)

    def currentBranch(self):
        """Get the current branch.

        Returns:
            str: The current branch.
        """
        return self.git.branch("--show-current")

    def createBranch(self, branch: str, origin: str = "origin", track: bool = True):
        """Create a new branch.

        Args:
            branch (str): The name of the branch.
            origin (str): The name of the remote.
            track (bool): Whether to track the branch.
        """
        if track:
            self.git.checkout("-b", branch)
            self.git.push("-u", origin, branch)
        else:
            self.git.checkout("-b", branch)

    def remote(self, url: str, name: str = "origin"):
        """Add a remote to the Git repository.

        Args:
            url (str): The URL of the remote.
            name (str): The name of the remote.
        """
        self.git.remote("add", name, url)

    def remoteExists(self, name: str):
        if self.git == False:
            return False

        return name in [remote.name for remote in self.repo.remotes]

    def pushTo(self, branch: str, origin: str = "origin", upstream: bool = True):
        """Push the changes to the remote.

        Args:
            branch (str): The branch to push the changes to.
            origin (str): The name of the remote.
            upstream (bool): Whether to push the changes to the upstream branch.
        """
        if upstream:
            self.git.push("-u", origin, branch)
        else:
            self.git.push(origin, branch)

    def renameTo(self, new: str):
        """Rename the current branch to a new name.

        Args:
            new (str): The new name of the branch.
        """
        self.git.branch("-M", new)

    def hasChanges(self) -> bool:
        """Check if there are changes to the repository.

        Returns:
            bool: True if there are changes, False otherwise.
        """
        return self.git.status("--porcelain") != ""

    def checkout(self, branch: str):
        """Checkout to a branch.

        Args:
            branch (str): The name of the branch to checkout.
        """
        self.git.checkout(branch)

    def pull(self, remote: str = "origin", branch: str = None):
        """Pull changes from the remote repository.

        Args:
            remote (str): The name of the remote (default: origin).
            branch (str): The name of the branch to pull (default: current branch).

        Returns:
            str: The output from the pull command.
        """
        if branch:
            return self.git.pull(remote, branch)

        return self.git.pull(remote)

    def merge(self, branch: str):
        """Merge a branch into the current branch.

        Args:
            branch (str): The name of the branch to merge.
        """
        self.git.merge(branch, "--no-ff")

    def tagExists(self, tag_name: str) -> bool:
        """Check if a tag exists.

        Args:
            tag_name (str): The name of the tag.

        Returns:
            bool: True if tag exists, False otherwise.
        """
        try:
            self.git.rev_parse(tag_name)
            return True
        except:
            return False

    def createTag(self, tag_name: str, message: str = None):
        """Create a new tag.

        Args:
            tag_name (str): The name of the tag.
            message (str): Optional message for annotated tag.
        """
        if message:
            self.git.tag("-a", tag_name, "-m", message)
        else:
            self.git.tag(tag_name)

    def deleteTag(self, tag_name: str):
        """Delete a local tag.

        Args:
            tag_name (str): The name of the tag to delete.
        """
        self.git.tag("-d", tag_name)

    def deleteRemoteTag(self, tag_name: str, remote: str = "origin"):
        """Delete a remote tag.

        Args:
            tag_name (str): The name of the tag to delete.
            remote (str): The name of the remote (default: origin).
        """
        self.git.push(remote, "--delete", f":refs/tags/{tag_name}")

    def pushTag(self, tag_name: str, remote: str = "origin"):
        """Push a tag to remote.

        Args:
            tag_name (str): The name of the tag to push.
            remote (str): The name of the remote (default: origin).
        """
        self.git.push(remote, tag_name)

    @staticmethod
    def buildRepo(target):
        """Build the Git repository.

        Args:
            target (str): The path to the Git repository.

        Returns:
            git.Repo: The Git repository.
            bool: False if the Git repository does not exist.
        """
        try:
            return git.Repo(target, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            return False
