"""Module for command line interface implementation."""

import abc
import argparse
import os
import pathlib

from rename_media import api


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
    def _add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-d', '--directory', help='Directory with files to rename.', default=os.getcwd())
        parser.add_argument('-p', '--prefix', help='Prefix for file name.', default='')
        parser.add_argument('-s', '--suffix', help='Suffix for file name.', default='')

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
    def _api_method(cls):
        raise NotImplementedError()

    @classmethod
    def execute(cls, args):
        errors = 0

        for result in cls._api_method()(pathlib.Path(args.directory), args.prefix, args.suffix):
            if not result.error_str:
                print(f'✅ Success: Renamed "{result.old_name}" to "{result.new_name}"')
            else:
                print(f'❌ Error: "{result.old_name}" {result.error_str}')
                errors += 1

        return os.EX_OK if errors == 0 else 1


class ImageCmd(SubCommand):
    """Rename image files by EXIF date."""

    @classmethod
    def _name(cls) -> str:
        return 'image'

    @classmethod
    def _api_method(cls):
        return api.rename_images


class VideoCmd(SubCommand):
    """Rename video files by encoded date."""

    @classmethod
    def _name(cls) -> str:
        return 'video'

    @classmethod
    def _api_method(cls):
        return api.rename_videos


def init_subparser(subparser: argparse._SubParsersAction):
    ImageCmd.init_subparser(subparser)
    VideoCmd.init_subparser(subparser)
