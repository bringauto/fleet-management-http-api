import dataclasses
from typing import Type, Dict, Any
import argparse
import json


_EMPTY_VALUE = None


@dataclasses.dataclass
class PositionalArgInfo:
    name: str
    type:Type
    help: str


@dataclasses.dataclass(frozen=True)
class ScriptArgs:
    argvals: Dict[str,str]
    config: Dict[str,Any] = dataclasses.field(default_factory=dict)


def request_and_get_script_arguments(
    script_description: str,
    *positional_args: PositionalArgInfo,
    include_db_args: bool = True
    ) -> ScriptArgs:

    parser = _new_arg_parser(script_description)
    _add_positional_args_to_parser(parser, *positional_args)
    _add_config_arg_to_parser(parser)
    if include_db_args:
        _add_db_args_to_parser(parser)
    return _parse_arguments(parser)


def _add_config_arg_to_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("<config-file-path>", type=str, help="The path to the config file.")


def _add_db_args_to_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-usr", "--username", type=str, help="The username for the database server.", default=_EMPTY_VALUE, required=False
    )
    parser.add_argument(
        "-pwd", "--password", type=str, help="The password for the database server.", default=_EMPTY_VALUE, required=False
    )
    parser.add_argument(
        "-l", "--location", type=str, help="The location/address of the database", default=_EMPTY_VALUE, required=False
    )
    parser.add_argument(
        "-p", "--port", type=str, help="The database port number.", default=_EMPTY_VALUE, required=False
    )
    parser.add_argument(
        "-db", "--database-name", type=str, help="The name of the database.", default=_EMPTY_VALUE, required=False
    )


def _add_positional_args_to_parser(parser: argparse.ArgumentParser, *args: PositionalArgInfo) -> None:
    for arg in args:
        parser.add_argument(arg.name, type=arg.type, help=arg.help)


def _new_arg_parser(script_description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description=script_description)


def load_config_file(path: str) -> Dict[str,Any]:
    try:
        with open(path) as config_file:
            config = json.load(config_file)
            return config
    except:
        raise ConfigFileNotFound(f"Could not load config file from path '{path}'.")


def _parse_arguments(parser: argparse.ArgumentParser) -> ScriptArgs:
    args = parser.parse_args().__dict__
    config = load_config_file(args.pop("<config-file-path>"))
    db_config = config["database"]["connection"]
    for key in args:
        if args[key] == _EMPTY_VALUE: args[key] = db_config[key]
    return ScriptArgs(args, config)


class ConfigFileNotFound(Exception): pass