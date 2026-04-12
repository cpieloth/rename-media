"""Entry point for package."""

import argparse
import logging
import sys

from rename_media.adapters import cmdline


def main(argv=None) -> int:
    """
    Start the Example tool.

    :return: 0 on success.
    """
    if not argv:
        argv = sys.argv

    # Init logging for CLI
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR, stream=sys.stderr)

    # Parse arguments
    parser = argparse.ArgumentParser(prog=argv[0])

    subparser = parser.add_subparsers(title='rename-media commands', description='Valid rename-media commands.')
    cmdline.init_subparser(subparser)

    args = parser.parse_args(argv[1:])
    try:
        # Check if a sub-command is given, otherwise print help.
        getattr(args, 'func')  # noqa: B009
    except AttributeError:
        parser.print_help()
        return 64  # windows compatibility aka os.EX_USAGE

    try:
        return args.func(args)
    except Exception as ex:  # noqa: BLE001
        print(ex, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
