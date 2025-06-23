import logging
from ipaddress import IPv4Address
from typing import Sequence, Optional

from hue_entertainment_pykit.lowl.clients.bridge_client import BridgeClient
from hue_entertainment_pykit.lowl.exceptions.link_button_not_pressed_exception import LinkButtonNotPressedError
from hue_entertainment_pykit.lowl.exceptions.low_hepk_exceptions import LoadingDataError, BridgeDiscoveryError, \
    BridgeApiError
from hue_entertainment_pykit.lowl.models.bridge.bridge_api_hue import BridgeApiHue
from hue_entertainment_pykit.lowl.models.bridge.bridge_combination_hue import BridgeCombinationHue
from hue_entertainment_pykit.lowl.models.bridge.bridge_config_hue import BridgeConfigHue
from hue_entertainment_pykit.lowl.models.bridge.bridge_device_hue import BridgeDeviceHue
from hue_entertainment_pykit.lowl.models.bridge.bridge_hue import BridgeHue
from hue_entertainment_pykit.lowl.utils.file_handler_util import FileHandlerUtil


logger = logging.getLogger(__name__)

class BridgeBuilderUtil:
    __MIN_SWVERSION = 1948086000

    @staticmethod
    def build_with_app_registration(ip_address: IPv4Address,
                                    application_name: Optional[str]) -> BridgeCombinationHue:
        try:
            bridge_api: BridgeApiHue = BridgeClient.generate_api_keys(ip_address, application_name)
            FileHandlerUtil.save_bridge_api(ip_address, bridge_api)
            bridge_config: BridgeConfigHue = BridgeClient.fetch_config(ip_address, bridge_api.username)
            bridge: BridgeHue = BridgeClient.fetch_bridge(ip_address, bridge_api.username)
            bridge_device: BridgeDeviceHue = BridgeClient.fetch_device(ip_address,
                                                                       bridge_api.username,
                                                                       bridge.owner.rid)

            return BridgeCombinationHue(ip_address=ip_address,
                                        bridge=bridge,
                                        device=bridge_device,
                                        config=bridge_config,
                                        api=bridge_api,
                                        does_support_streaming=int(bridge_config.swversion) >=
                                                               BridgeBuilderUtil.__MIN_SWVERSION)
        except LinkButtonNotPressedError as e:
            logger.error(e)
            raise LinkButtonNotPressedError() from e
        except Exception as e:
            logger.error(e)
            raise BridgeApiError(f"Failed to create bridge from IP address {ip_address}") from e

    @staticmethod
    def build_without_app_registration(ip_address: IPv4Address) -> BridgeCombinationHue:
        try:
            bridge_api: BridgeApiHue = FileHandlerUtil.load_bridge_api(ip_address)
        except FileNotFoundError as e:
            logger.warning('No existing bridge API data found: %s', e)
            raise LoadingDataError(f"No existing bridge API data found.")
        except Exception as e:
            logger.error('Failed to read bridge API: %s', e)
            raise LoadingDataError(f"Failed to read bridge API.")

        try:
            bridge_config: BridgeConfigHue = BridgeClient.fetch_config(ip_address, bridge_api.username)
            bridge: BridgeHue = BridgeClient.fetch_bridge(ip_address, bridge_api.username)
            bridge_device: BridgeDeviceHue = BridgeClient.fetch_device(ip_address,
                                                                       bridge_api.username,
                                                                       bridge.owner.rid)

            return BridgeCombinationHue(ip_address=ip_address,
                                        bridge=bridge,
                                        device=bridge_device,
                                        config=bridge_config,
                                        api=bridge_api,
                                        does_support_streaming=int(bridge_config.swversion) >=
                                                               BridgeBuilderUtil.__MIN_SWVERSION)
        except Exception as e:
            logger.error(e)
            raise BridgeApiError(f"Failed to create bridge from IP address {ip_address}") from e

    @staticmethod
    def __filter_supported_bridges(bridges: Sequence[BridgeCombinationHue]) -> list[BridgeCombinationHue]:
        """
        Filters the given list of bridges to only include those that support streaming.

        Parameters:
            bridges (Sequence[BridgeHue]): A list of Bridge instances.

        Returns:
            list[Bridge]: A filtered list of Bridge instances supporting streaming.
        """

        return [bridge for bridge in bridges if BridgeBuilderUtil.__does_support_streaming(bridge)]

    @staticmethod
    def __does_support_streaming(bridge: BridgeCombinationHue) -> bool:
        """
        Checks if a given clients supports streaming based on its software version.

        Parameters:
            bridge (BridgeHue): An instance of the Bridge class.

        Returns:
            bool: True if the clients supports streaming, False otherwise.
        """

        return int(bridge.config.swversion) >= BridgeBuilderUtil.__MIN_SWVERSION

    @staticmethod
    def get_min_swversion() -> int:
        return BridgeBuilderUtil.__MIN_SWVERSION
