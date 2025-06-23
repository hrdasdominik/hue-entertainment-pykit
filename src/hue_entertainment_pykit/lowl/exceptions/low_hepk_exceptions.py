class LowHepkError(Exception):
    """Base class for all LowHepk exceptions."""

class FetchLightsError(LowHepkError):
    """Failed to fetch light/s."""

class BridgeDiscoveryError(LowHepkError):
    """Failed to find any bridge, or all failed to respond."""

class ConfigurationFetchError(LowHepkError):
    """Failed to fetch entertainment configuration."""

class StreamStartError(LowHepkError):
    """Failed to start Hue Entertainment stream."""

class StreamStopError(LowHepkError):
    """Failed to stop Hue Entertainment stream."""

class EncodingLightDataError(LowHepkError):
    """Failed to encode light data."""

class LoadingDataError(LowHepkError):
    """Failed to load data."""

class BridgeApiError(LowHepkError):
    """Failed while requesting through bridge API."""