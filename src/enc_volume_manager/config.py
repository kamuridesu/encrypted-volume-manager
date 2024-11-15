import yaml
from dataclasses import dataclass
from typing import Self

from src.enc_volume_manager.custom_types import Base


@dataclass
class Volume(Base):
    folder: str
    name: str
    mount_point: str
    size: str


@dataclass
class Bitwarden(Base):
    url: str
    password_base64: str
    credential_name: str


@dataclass
class Folder(Base):
    name: str
    children: list[Self]


@dataclass
class Config(Base):
    veracrypt_executable_path: str
    volume: Volume
    default_structure: list[Folder]
    bitwarden: Bitwarden


def load_config(file_path: str) -> Config:
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        return Config.parse(data)
