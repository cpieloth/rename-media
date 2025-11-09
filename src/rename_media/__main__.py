"""Entry point for package."""

import sys

import rename_media.cmdline


def main() -> int:
    """Execute the CLI entry point."""
    return rename_media.cmdline.main()


if __name__ == '__main__':
    sys.exit(main())
