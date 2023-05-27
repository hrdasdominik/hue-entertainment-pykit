"""_summary_"""

from services.philips_bridge_service import PhilipsBridgeService


class PhilipsBridgeController:
    """_summary_"""

    def __init__(self, bridge_service: PhilipsBridgeService) -> None:
        self.__bridge_service = bridge_service

    def print_config(self):
        """_summary_"""
        self.__bridge_service.print_config()
