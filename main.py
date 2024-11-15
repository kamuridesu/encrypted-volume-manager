import yaml
from dataclasses import dataclass
from typing import Any, Callable, Self
from pathlib import Path


class Base:
    @classmethod
    def parse(
        cls: Any,
        data: dict[str, Any],
        external_fields: dict[str, Callable[[dict[Any, Any]], Any]] = {},
    ) -> Any:
        if data is None:
            return
        kwargs: dict[str, Any] = {}
        for field in cls.__dict__.get("__match_args__", []):
            value = data.get(field)
            if (f := external_fields.get(field)) is not None and value is not None:
                value = f(value)
            kwargs[field] = value
        return cls(**kwargs)


@dataclass
class Volume(Base):
    folder: str
    name: str

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Any:
        return super().parse(data)


@dataclass
class Folder(Base):
    name: str
    children: list[Self]

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Any:
        return super().parse(
            data,
            {
                "children": lambda x: [Folder.parse(folder) for folder in x],
            },
        )


@dataclass
class Config(Base):
    volume: Volume
    default_structure: list[Folder]

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Self:
        return super().parse(
            data,
            {
                "volume": Volume.parse,
                "default_structure": lambda x: [Folder.parse(folder) for folder in x],
            },
        )


def load_config(file_path: str) -> Config:
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        return Config.parse(data)


def create_folder_structure(folder: Folder, parent: Path = Path(".")):
    folder_ = parent / folder.name
    print(f"Creating folder {folder_}")
    folder_.mkdir(exist_ok=True)
    if not folder.children:
        return
    for child in folder.children:
        create_folder_structure(child, parent / folder.name)


config = load_config("config.yaml")

create_folder_structure(config.default_structure[0])
