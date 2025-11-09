"""Module for command line interface implementation."""

import abc
import argparse
import logging
import os
import pathlib
import sys

import rename_media.image


class SubCommand(abc.ABC):
    """
    Abstract base class for sub commands.

    A new sub command can be added by calling the init_subparser().
    """

    @classmethod
    @abc.abstractmethod
    def _name(cls) -> str:
        """
        Return name of the command.

        :return: Command name
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def _help(cls) -> str:
        """
        Return help description.

        :return: Help description
        :rtype: str
        """
        return str(cls.__doc__)

    @classmethod
    @abc.abstractmethod
    def _add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """
        Initialize the argument parser and help for the specific sub-command.

        Must be implemented by a sub-command.

        :param parser: A parser.
        :type parser: argparse.ArgumentParser
        :return: void
        """
        raise NotImplementedError()

    @classmethod
    def init_subparser(cls, subparsers: argparse._SubParsersAction) -> None:
        """
        Initialize the argument parser and help for the specific sub-command.

        :param subparsers: A subparser.
        :type subparsers: argparse.ArgumentParser
        :return: void
        """
        parser = subparsers.add_parser(cls._name(), help=cls._help())
        cls._add_arguments(parser)
        parser.set_defaults(func=cls.execute)

    @classmethod
    @abc.abstractmethod
    def execute(cls, args):
        """
        Execute the command.

        Must be implemented by a sub-command.

        :param args: argparse arguments.
        :return: 0 on success.
        """
        raise NotImplementedError()


class ImageCmd(SubCommand):
    """Rename image files by EXIF date."""

    @classmethod
    def _name(cls) -> str:
        return 'image'

    @classmethod
    def _add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-d', '--directory', help='Directory with image files to rename.', default=os.getcwd())
        parser.add_argument('-p', '--prefix', help='Prefix for file name.', default='')
        parser.add_argument('-s', '--suffix', help='Suffix for file name.', default='')

    @classmethod
    def execute(cls, args) -> int:
        errors = 0

        for result in rename_media.image.rename_with_date(pathlib.Path(args.directory), args.prefix, args.suffix):
            if result.result:
                print(f'✅ Renamed: "{result.old_name}" to "{result.new_name}"')
            else:
                print(f'❌ Error: "{result.old_name}"')
                errors += 1

        return os.EX_OK if errors == 0 else 1


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
    ImageCmd.init_subparser(subparser)

    args = parser.parse_args(argv[1:])
    try:
        # Check if a sub-command is given, otherwise print help.
        getattr(args, 'func')
    except AttributeError:
        parser.print_help()
        return 64  # windows compatibility aka os.EX_USAGE

    try:
        return args.func(args)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        print(ex, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
