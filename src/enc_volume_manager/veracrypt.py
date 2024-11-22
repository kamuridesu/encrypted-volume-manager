import os
import sys
import asyncio

from src.enc_volume_manager.config import Volume
from src.enc_volume_manager.utils import generate_random_seed_file, Commands


class Veracrypt:
    def __init__(self, executable_path: str, config: Volume) -> None:
        self.executable_path = executable_path
        self.config = config

    def __get_create_executable(self):
        if sys.platform == "win32":
            return os.path.join(self.executable_path, "VeraCrypt Format.exe")
        return os.path.join(self.executable_path, "veracrypt")
    
    def __get_mount_executable(self):
        if sys.platform == "win32":
            return os.path.join(self.executable_path, "VeraCrypt.exe")
        return os.path.join(self.executable_path, "veracrypt")
    
    def __umount(self, target: str) -> list[str]:
        return Commands["UNMOUNT"].format(TARGET=target).split(" ")
    
    async def unmount(self):
        unmount_executable = self.__get_mount_executable()

        command = self.__umount(self.config.mount_point)
        
        p = await asyncio.create_subprocess_exec(unmount_executable, *command, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        await p.communicate()
        if p.returncode != 0:
            print(f"Error unmounting volume: {p.stderr}")
            raise Exception("Error unmounting volume")
        print(f"Volume '{self.config.name}' unmounted successfully")

    def __mount(self, volume: str, target: str, password: str) -> list[str]:
        return Commands["MOUNT"].format(VOLUME=volume, TARGET=target, PASSWORD=password).split(" ")
    
    async def mount(self, password: str): 
        mount_executable = self.__get_mount_executable()
        folder = self.config.folder
        name = self.config.name

        command = self.__mount(os.path.join(folder, name), self.config.mount_point, password)

        p = await asyncio.create_subprocess_exec(mount_executable, *command, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        await p.communicate()
        if p.returncode != 0:
            print(f"Error mounting volume: {p.stderr}")
            raise Exception("Error mounting volume")
        print(f"Volume '{name}' mounted successfully")

    def __create(self, volume: str, password: str, size: str, random_source: str | None) -> list[str]:
        kwargs = {
            "VOLUME": volume,
            "PASSWORD": password,
            "SIZE": size,
        }
        if random_source:
            kwargs["RANDOM_SOURCE"] = random_source
        return Commands["CREATE"].format(**kwargs).split(" ")

    async def create(self, password: str):
        create_executable = self.__get_create_executable()
        size = self.config.size
        folder = self.config.folder
        name = self.config.name
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        random_seed_file = generate_random_seed_file()

        command = self.__create(os.path.join(folder, name), password, size, str(random_seed_file))

        p = await asyncio.create_subprocess_exec(create_executable, *command, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        await p.communicate()
        random_seed_file.unlink(missing_ok=True)
        if p.returncode != 0:
            print(f"Error creating volume: {p.stderr}")
            raise Exception("Error creating volume")
        print(f"Volume '{name}' created successfully on '{os.path.abspath(folder)}'")
