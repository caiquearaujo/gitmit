import os
import tempfile
import subprocess

from src.gitmit import __VERSION__
from src.gitmit.utils.terminal import display_info, display_success, display_warning


def main():
    version = __VERSION__
    dist_dir = os.path.join(tempfile.gettempdir(), "gitmit")

    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
        display_info(f"Directory '{dist_dir}' created.")

    output_file = os.path.join(dist_dir, f"gitmit-{version}.pex")

    cmd = [
        "pex",
        ".",
        "-o",
        output_file,
        "-e",
        "gitmit:main",
        "--python-shebang",
        "/usr/bin/env python3",
    ]

    subprocess.run(cmd)
    display_success(f"Build completed successfully: {output_file}")
    display_warning(
        f"a) Move file: [bold purple]mv {output_file} /usr/local/bin/gitmit[/bold purple]"
    )
    display_warning(
        f"b) Make file executable: [bold purple]chmod +x /usr/local/bin/gitmit[/bold purple]"
    )


if __name__ == "__main__":
    main()
