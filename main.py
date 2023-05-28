"""_summary_"""
from api.bridge.bridge import Bridge
from api.light.light_model import Light
from api.light.light_repository import LightRepository


def main():
    """_summary_"""
    bridge = Bridge().get_ip_with_broker()
    light_repository = LightRepository(bridge).generate_key()
    lights: list[Light] = light_repository.get_lights()

    for light in lights:
        light.on = False

        light_repository.put_light(light)


if __name__ == "__main__":
    main()
