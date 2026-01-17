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
    requirements_file = os.path.join(dist_dir, "requirements.txt")

    # Export dependencies using uv
    display_info("Exporting dependencies...")
    export_result = subprocess.run(
        ["uv", "export", "--no-hashes", "--no-dev", "--no-emit-project"],
        capture_output=True,
        text=True,
    )

    if export_result.returncode != 0:
        raise RuntimeError(f"Failed to export dependencies: {export_result.stderr}")

    # Filter out the "Resolved X packages" line from stderr
    requirements = export_result.stdout
    with open(requirements_file, "w") as f:
        f.write(requirements)

    # Build PEX using uvx
    display_info("Building PEX executable...")
    cmd = [
        "uvx",
        "pex",
        "-r",
        requirements_file,
        "-o",
        output_file,
        "-e",
        "gitmit:main",
        "--python-shebang",
        "/usr/bin/env python3",
        "--no-transitive",
        "--sources-dir=src",
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        raise RuntimeError("Failed to build PEX executable")

    # Cleanup temporary requirements file
    os.remove(requirements_file)

    display_success(f"Build completed successfully: {output_file}")
    display_warning(
        f"a) Move file: [bold purple]mv {output_file} /usr/local/bin/gitmit[/bold purple]"
    )
    display_warning(
        f"b) Make file executable: [bold purple]chmod +x /usr/local/bin/gitmit[/bold purple]"
    )


if __name__ == "__main__":
    main()
