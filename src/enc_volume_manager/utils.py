import sys
import random
from datetime import datetime
from pathlib import Path
from typing import TypedDict


def generate_random_seed_file() -> Path:
    """Should generate a tmp seed file with random content to encrypt data, should be at least 64 bytes long"""
    seed = random.getrandbits(512)
    seed = seed.to_bytes(64, "big")
    seed = seed.hex()
    seed_file = Path(f"seed_{datetime.now().isoformat()}.seed")
    with seed_file.open("w") as f:
        f.write(seed)
    return seed_file


def get_driver_path(path: str) -> Path:
    if sys.platform == "win32":
        return Path(f"{path}:\\")
    return Path(path)


CommandsType = TypedDict("CommandsType", {
    "CREATE": str,
    "MOUNT": str,
    "UNMOUNT": str
})
CommandsLinux: CommandsType = {
    "MOUNT": "-t --mount {VOLUME} {TARGET} --password {PASSWORD} --pim 0 --protect-hidden no --slot 1 --keyfiles ",
    "UNMOUNT": "-t -d {TARGET}",
    "CREATE": "-t -c {VOLUME} --password {PASSWORD} --hash sha512 --filesystem FAT --size {SIZE} --force --random-source {RANDOM_SOURCE} --volume-type normal --encryption AES --pim 0 --keyfiles "
}
CommandsWindows: CommandsType = {
    "MOUNT": "/v {VOLUME} /password {PASSWORD} /l {TARGET} /q",
    "UNMOUNT": "/d {TARGET} /q",
    "CREATE": "/create {VOLUME} /password {PASSWORD} /hash sha512 /filesystem FAT /size {SIZE} /force"
}
Commands = CommandsLinux if sys.platform != "win32" else CommandsWindows
