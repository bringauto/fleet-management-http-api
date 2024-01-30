import dataclasses
from typing import Type, Dict, Any
import argparse
import json

from fleet_management_api.script_args.configs import APIConfig as _APIConfig


_EMPTY_VALUE = None


@dataclasses.dataclass
class PositionalArgInfo:
    name: str
    type:Type
    help: str


@dataclasses.dataclass(frozen=True)
class ScriptArgs:
    argvals: Dict[str,str]
    config: _APIConfig


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
    parser.add_argument(
        "-t", "--test", type=str, help="Connect to a sqlite database. Username and password are ignored.", default="", required=False
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
    config_path = args.pop("<config-file-path>")
    try:
        config = _APIConfig(**load_config_file(config_path))
    except Exception as e:
        print(f"\nCheck the configuration file ('{config_path}').\n")
        raise e
    _update_config_with_args(args, config)
    return ScriptArgs(args, config)


def _update_config_with_args(args:Dict[str, Any], config: _APIConfig) -> None:
    if args["username"] != _EMPTY_VALUE:
        config.database.connection.username = args["username"]
    if args["password"] != _EMPTY_VALUE:
        config.database.connection.password = args["password"]
    if args["location"] != _EMPTY_VALUE:
        config.database.connection.location = args["location"]
    if args["port"] != _EMPTY_VALUE:
        config.database.connection.port = args["port"]
    if args["database_name"] != _EMPTY_VALUE:
        config.database.connection.database_name = args["database_name"]


class ConfigFileNotFound(Exception): pass