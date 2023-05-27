"""This module is for holding config and keys which actually should be uploaded to the github"""

IP_BRIDGE = "192.168.100.11"
ID_BRIDGE = "ecb5fafffe9779da"

API_KEY = "Z4CIRp2kbqfQafVeKK8P7mwuVl1bJYVL08BgWxcm"
URL_HTTP = f"http://{IP_BRIDGE}/api/{API_KEY}"
URL_HTTPS = f"https://{IP_BRIDGE}/api/{API_KEY}"

API2_URL_HTTP = f"http://{IP_BRIDGE}/clip/v2/"
API2_URL_HTTPS = f"https://{IP_BRIDGE}/clip/v2/"
API2_USERNAME = "Jwa4fUSGRFmhmfiesGsU9XvazrH623UlImJGYIFI"
API2_CLIENTKEY = "59C827D5E3A44EE17F7B6167442C5D22"

REQUESTS_CA_BUNDLE = "config/huebridge_cacert.pem"
