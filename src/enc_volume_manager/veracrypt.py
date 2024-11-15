import os
import sys
import random
import asyncio

from enc_volume_manager.config import Volume


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
    
    async def unmount(self):
        unmount_executable = self.__get_mount_executable()

        command = []

        if sys.platform == "win32":
            command = [
                "/d",
               self.config.mount_point,
                "/q"
            ]
        
        p = await asyncio.create_subprocess_exec(unmount_executable, *command, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        await p.communicate()
        if p.returncode != 0:
            print(f"Error unmounting volume: {p.stderr}")
            raise Exception("Error unmounting volume")
        print(f"Volume {self.config.name} unmounted successfully")
    
    async def mount(self, password: str): 
        mount_executable = self.__get_mount_executable()
        folder = self.config.folder
        name = self.config.name

        command = []

        if sys.platform == "win32":
            command = [
                "/v",
                os.path.join(folder, name),
                "/password",
                password,
                "/l",
                self.config.mount_point,
                "/q"
            ]
        
        p = await asyncio.create_subprocess_exec(mount_executable, *command, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        await p.communicate()
        if p.returncode != 0:
            print(f"Error mounting volume: {p.stderr}")
            raise Exception("Error mounting volume")
        print(f"Volume {name} mounted successfully")


    async def create(self, password: str):
        create_executable = self.__get_create_executable()
        size = self.config.size
        folder = self.config.folder
        name = self.config.name
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        command = []

        if sys.platform == "win32":
            command = [
                "/create",
                os.path.join(folder, name),
                "/password",
                password,
                "/hash",
                "sha512",
                "/filesystem",
                "FAT",
                "/size",
                size,
                "/force"
            ]

            print(command)
        
        p = await asyncio.create_subprocess_exec(create_executable, *command, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        await p.communicate()
        if p.returncode != 0:
            print(f"Error creating volume: {p.stderr}")
            raise Exception("Error creating volume")
        print(f"Volume {name} created successfully")
