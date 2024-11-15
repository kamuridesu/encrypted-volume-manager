from pathlib import Path
from src.enc_volume_manager.config import load_config, Folder
from src.enc_volume_manager.bitwarden import Bitwarden
from src.enc_volume_manager.veracrypt import Veracrypt
from src.enc_volume_manager.utils import get_driver_path


def create_folder_structure(folder: Folder, parent: Path = Path(".")):
    folder_ = parent / folder.name
    print(f"Creating folder {folder_}")
    folder_.mkdir(exist_ok=True)
    if not folder.children:
        return
    [create_folder_structure(child, parent / folder.name) for child in folder.children]


async def main():
    config = load_config("config.yaml")
    bitwarden = Bitwarden(config.bitwarden)
    await bitwarden.unlock()
    password = await bitwarden.get_password()
    await bitwarden.lock()
    if not password:
        raise Exception("Password not found")
    veracrypt = Veracrypt(config.veracrypt_executable_path, config.volume)
    await veracrypt.create(password)
    await veracrypt.mount(password)
    create_folder_structure(config.default_structure[0], get_driver_path(config.volume.mount_point))
    input("Press enter to unmount")
    await veracrypt.unmount()
    print("Done")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    # main()
