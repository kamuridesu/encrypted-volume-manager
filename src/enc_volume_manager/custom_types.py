import json
from typing import TypeVar, Callable, Any, Type, get_origin, get_args, Self

T = TypeVar("T", bound="Base")
self_checker = lambda annotation: annotation is Self


class Base:
    @classmethod
    def __get_parse_method(cls: Type[T], field: str) -> Callable[[dict[str, Any]], T] | None:
        """Retrieve the parse method for a field's type if it exists."""
        annotation = cls.__annotations__.get(field)
        if get_origin(annotation) == list:
            annotation = get_args(annotation)[0]
            if self_checker(annotation):
                annotation = cls
        return getattr(annotation, "parse", None)

    @classmethod
    def parse(cls: Type[T], data: dict[str, Any]) -> T :
        """Parse a dictionary into an instance of the class."""
        kwargs = {}
        for field in cls.__dict__.get("__match_args__", []):
            value = data.get(field)
            parse_method = cls.__get_parse_method(field)
            if value is not None and parse_method:
                value = (
                    [parse_method(item) for item in value]
                    if isinstance(value, list)
                    else parse_method(value)
                )
            kwargs[field] = value
        return cls(**kwargs)

    def as_dict(self) -> dict[str, Any]:
        """Convert the instance into a dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if hasattr(value, "as_dict"):
                result[key] = value.as_dict()
            elif isinstance(value, list) and all(hasattr(item, "as_dict") for item in value):
                result[key] = [item.as_dict() for item in value]
            else:
                result[key] = value
        return result

    def as_json(self, indent=4, ensure_ascii=False) -> str:
        """Convert the instance into a JSON string."""
        return json.dumps(self.as_dict(), indent=indent, ensure_ascii=ensure_ascii)
