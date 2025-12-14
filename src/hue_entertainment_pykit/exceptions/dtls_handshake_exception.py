"""
Defines the DTLSHandshakeException class, a custom exception for handling errors related to DTLS handshake operations.
It is utilized for capturing and reporting various error conditions during interactions with the Hue Bridge.
"""


class DTLSHandshakeException(Exception):
    """
    Custom exception class for errors related to DTLS handshake.

    This class extends the base Exception class to provide a more specific exception type for handling errors
    encountered during interactions with the Philips Hue Bridge.
    """
