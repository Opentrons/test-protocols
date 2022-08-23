"""From base"""

from opentrons import protocol_api

metadata = {
    "protocolName": "🛠 Test requests 🛠",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": ("Put a description here."),
    "apiLevel": "2.12",
}

import requests

HEADERS = {"Accept": "application/json", "Content-type": "application/json"}


class ZippopotamClient:
    """
    client for the zippopotam rest api
    """

    def __init__(self, base_url):
        self.base_url = f"http://{base_url}"
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def get_us_by_zip(self, zip_code: str):
        """
        retrieve place data for the united states (us) by zip code
        """
        endpoint = f"{self.base_url}/us/{zip_code}"
        return self.session.get(endpoint, timeout=5)


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    zippo_client = ZippopotamClient("api.zippopotam.us")
    response = zippo_client.get_us_by_zip("66049")
    ctx.comment(response.status_code)
    ctx.comment(str(response.json()))
