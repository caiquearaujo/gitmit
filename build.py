import os
import argparse
import zipapp
import tempfile

from src.utils.terminal import display_info, display_success, display_warning


def main():
    parser = argparse.ArgumentParser(
        description="Create a zipapp with a version suffix."
    )

    parser.add_argument(
        "-v",
        "--version",
        required=True,
        help="Version of the build (eg: 1.0.0)",
    )

    args = parser.parse_args()

    dist_dir = os.path.join(tempfile.gettempdir(), "gitmit")

    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
        display_info(f"Directory '{dist_dir}' created.")

    output_file = os.path.join(dist_dir, f"gitmit-{args.version}.pyz")

    zipapp.create_archive(
        source=".",
        target=output_file,
        main="gitmit:main",
        interpreter="/usr/bin/env python3",
    )

    display_success(f"Build completed successfully: {output_file}")
    display_warning(
        f"a) Move file: [bold purple]mv {output_file} /usr/local/bin/gitmit[/bold purple]"
    )
    display_warning(
        f"b) Make file executable: [bold purple]chmod +x /usr/local/bin/gitmit[/bold purple]"
    )


if __name__ == "__main__":
    main()
