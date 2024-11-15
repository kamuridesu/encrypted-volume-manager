import os
import aiohttp

from base64 import b64decode
from src.enc_volume_manager.config import Bitwarden as BitwardenConfig


class Bitwarden:
    def __init__(self, config: BitwardenConfig) -> None:
        self.config = config
        self.server_url = config.url
        self.session = ""
        self.locked = True

    async def lock(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.server_url}/lock") as response:
                if response.status == 200:
                    self.locked = True
                    os.environ.pop("BW_SESSION")
                    return True
                return False
            
    async def unlock(self):
        password = b64decode(self.config.password_base64).decode()
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.server_url}/unlock", json={"password": password}) as response:
                if response.status == 200:
                    self.locked = False
                    self.session = (await response.json())["data"]["raw"]
                    os.environ["BW_SESSION"] = self.session
                    return True
                raise Exception(await response.text())
            
    async def list_items(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.server_url}/list/object/items") as response:
                if response.status == 200:
                    return await response.json()
                raise Exception(await response.text())

    async def get_item(self, id: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.server_url}/object/item/{id}") as response:
                if response.status == 200:
                    return self.__get_password(await response.json())
                raise Exception(await response.text())
            
    async def get_item_by_name(self, name: str):
        items = await self.list_items()
        for item in items["data"]["data"]:
            if item.get("name") == name:
                return self.__get_password({'data': item})
        return None
    
    async def get_password(self) -> str | None:
        return await self.get_item_by_name(self.config.credential_name)

    def __get_password(self, item: dict) -> str:
        password = item.get("data", {}).get("login", {}).get("password", None)
        if password is None:
            password = item.get("data", {}).get("notes", "")
        return password
