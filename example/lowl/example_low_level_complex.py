import random
import time
import threading
from ipaddress import IPv4Address

from hue_entertainment_pykit import LowHepk
from hue_entertainment_pykit.lowl.enums.log_level_enum import LogLevelEnum
from hue_entertainment_pykit.lowl.models.bridge.hue.bridge_combination_hue import BridgeCombinationHue


def main():
    LowHepk.configure_logs(LogLevelEnum.DEBUG)
    bridges: list[BridgeCombinationHue] = LowHepk.discover_bridges(ip_addresses=[IPv4Address('192.168.1.204')])
    bridge = bridges[0]

    entertainments = LowHepk.fetch_entertainment_configurations(bridge.ip_address, bridge.api.username)
    pc_area_ent = entertainments[0]

    lights = LowHepk.fetch_lights_from_entertainment_configuration(bridge.ip_address, bridge.api.username, pc_area_ent.id)

    with LowHepk.start_stream(bridge.ip_address,
                              bridge.api.username,
                              bridge.api.clientkey,
                              pc_area_ent.id) as dtls_connection:

        send_lock = threading.Lock()

        def light_worker(light, sleep_s: float):
            while True:
                light.set_colors(random.random(), random.random(), random.random())
                with send_lock:
                    LowHepk.send_message_to_bridge(pc_area_ent.id, dtls_connection, [light])
                time.sleep(sleep_s)

        threads = []
        for idx, light in enumerate(lights):
            sleep_s = 0.5 + random.random() * 2.0
            t = threading.Thread(target=light_worker, args=(light, sleep_s), daemon=True, name=f"light-{idx}")
            t.start()
            threads.append(t)

        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()