import asyncio
import json
import random

import websockets

async def stream_data(websocket, path):
    with open("hue-emu.json", "r") as f:
        data_list = json.loads(f.read())
    while True:
        for item in data_list:
            item["brightness"] = random.randint(0, 100)
            item["color"] = [random.randint(0, 255),
                             random.randint(0, 255),
                             random.randint(0, 255)]
            x = round(random.uniform(-1, 1), 3)
            y = round(random.uniform(-1, 1), 3)
            z = round(random.uniform(-1, 1), 3)
            item["position"] = {"x": f"{x}", "y": f"{y}", "z": f"{z}"}
        await websocket.send(json.dumps(data_list))
        await asyncio.sleep(6)  # Adjust the sleep time as needed


if __name__ == "__main__":
    start_server = websockets.serve(stream_data, "localhost", 80)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
