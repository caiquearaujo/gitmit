import os
import shutil
import sys
import uuid

import requests
from rich.progress import Progress

from ..utils.terminal import display_error, display_success


class UpdateTool:
    """Update tool."""

    def __init__(self, version: str, repo: str = "caiquearaujo/gitmit"):
        """Initialize the update tool."""
        self.version: str = version
        self.repo: str = repo

    def run(self, force: bool = False):
        """Run the update tool."""
        response = requests.get(
            f"https://api.github.com/repos/{self.repo}/releases/latest"
        )

        if response.status_code != 200:
            display_error("Cannot fetch the latest version from GitHub.")
            return

        release_info: dict[str, str] = response.json()
        latest_version = release_info.get("tag_name")
        current_version = self.version

        if latest_version == current_version and not force:
            display_success("You are already on the latest version.")
            return

        asset_url = f"https://github.com/{self.repo}/releases/download/{latest_version}/gitmit-{latest_version}.pex"
        temp_path = f"/tmp/gitmit-{uuid.uuid4()}.pex"

        self.__download(asset_url, temp_path)

        try:
            shutil.copy(temp_path, sys.argv[0])
            os.chmod(sys.argv[0], 0o755)
            display_success("Update successful!")
        except Exception as e:
            display_error(f"Error updating the file: {e}")

    def __download(self, url: str, destination: str):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("Content-Length", 0))

        with open(destination, "wb") as file, Progress() as progress:
            task = progress.add_task("[green]Downloading...", total=total_size)
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    progress.update(task, advance=len(chunk))
