import asyncio
import logging
import time

import aiohttp
from aiohttp import ClientResponse

from api.light.light_model import Light
from api.light.light_repository import LightRepository
from api.utils.decorators import singleton


@singleton
class LightService:
    def __init__(self, light_repository: LightRepository):
        self._light_repository = light_repository

    async def update_lights(self):
        logging.debug("Started 'update_lights'")
        lights: list[Light] = self._light_repository.get_lights()

        results = []

        start = time.time()
        async with aiohttp.ClientSession() as session:
            tasks = []
            for light in lights:
                if not light.on.on:
                    light.on.on = True
                light.color.xy = {"x": 0.3, "y": 0.2}

                tasks.append(self._light_repository.put_light(light, session))

            responses: list[ClientResponse] = await asyncio.gather(*tasks)
            for response in responses:
                print(response.reason)
                result = await response.json()
                logging.debug(f"Response: {result}")
                results.append(result)

        end = time.time()
        total_time = end - start
        print(f"Total time: {total_time}")
